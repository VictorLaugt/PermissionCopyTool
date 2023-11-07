from __future__ import annotations
from typing import Callable

from pathlib import Path
import os
import stat

import pickle


# ---- file exploration
def permissions(path: Path) -> int:
    return os.stat(path).st_mode

class Exploration:
    def __init__(self, root_dir: Path):
        self._root_dir = root_dir
    
    @classmethod
    def _explore(cls, path: Path, callback: Callable[[Path], None]):
        callback(path)
        if path.is_dir() and os.access(path, os.R_OK):
            for subpath in path.iterdir():
                cls._explore(subpath, callback)
    
    def explore(self, callback: Callable[[Path], None]):
        return self._explore(self._root_dir, callback)
    
    def get_paths(self) -> list[Path]:
        path_list = []
        def add_entry(path):
            path_list.append(path)

        self._explore(self._root_dir, add_entry)
        return path_list
            
    def get_paths_and_perms(self) -> dict[Path, int]:
        perm_dict = {}
        def add_entry(path):
            perm_dict[path.relative_to(self._root_dir)] = permissions(path)
            
        self._explore(self._root_dir, add_entry)
        return perm_dict
    

# ---- permission management
# Mask to retrieve everything except the permission section in the `st_mode`
# field of the `stat` structure.
MODE_AND_TYPE_DATA = ~0o777

DEFAULT_FILE_PERMS = (
    stat.S_IRUSR | stat.S_IWUSR |
    stat.S_IRGRP | stat.S_IWGRP |
    stat.S_IROTH
)

DEFAULT_DIR_PERMS = (
    stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
    stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP |
    stat.S_IROTH                | stat.S_IXOTH
)

def with_permissions(st_mode: int, permission_mask: int) -> int:
    return (st_mode & MODE_AND_TYPE_DATA) | permission_mask

class PermPatch:
    def __init__(self):
        self.fullpaths: list[Path] = []
        self.perms: list[int] = []
    
    def __len__(self) -> int:
        return len(self.fullpaths)
    
    def append(self, p: Path, m: int) -> None:
        self.fullpaths.append(p)
        self.perms.append(m)
    
    def auto_fill(self, exploration: Exploration) -> None:
        def auto_perm(path):
            if path.is_file():
                self.append(path, with_permissions(permissions(path), DEFAULT_FILE_PERMS))
            elif path.is_dir():
                self.append(path, with_permissions(permissions(path), DEFAULT_DIR_PERMS))
        exploration.explore(auto_perm)
    
    def __repr__(self) -> str:
        rows = []
        for p, new_m in zip(self.fullpaths, self.perms):
            old_m = permissions(p)
            rows.append(f'[{stat.filemode(old_m)}] -> [{stat.filemode(new_m)}] {str(p)}')
        return '\n'.join(rows)
    
    def apply(self) -> None:
        for p, new_m in zip(self.fullpaths, self.perms):
            p.chmod(new_m)


# ---- tools
def perm_export(src_dir: Path, save_file: Path) -> None:
    perm_dict = Exploration(src_dir).get_paths_and_perms()
    with open(save_file, mode='wb') as file:
        pickle.dump(perm_dict, file)
        

def perm_import(dst_dir: Path, save_file: Path) -> PermPatch:
    paths = Exploration(dst_dir).get_paths()
    with open(save_file, mode='rb') as file:
        imported_paths_and_perms = pickle.load(file)
    
    patch = PermPatch()
    for path in imported_paths_and_perms.keys() & paths:
        fullpath = dst_dir.joinpath(path)
        new_perm = imported_paths_and_perms[path]
        old_perm = permissions(fullpath)
        if new_perm != old_perm:
            patch.append(fullpath, new_perm)
    
    return patch


def perm_auto_patch(dst_dir: Path) -> PermPatch:
    patch = PermPatch()
    patch.auto_fill(Exploration(dst_dir))
    return patch
