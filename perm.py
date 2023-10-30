from __future__ import annotations

from pathlib import Path
import os
from stat import filemode

import pickle


class Exploration:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
    
    def _explore(self, path: Path, perm_dict: dict[Path, int]):
        perm_dict[path.relative_to(self.root_dir)] = os.stat(path).st_mode
        if path.is_dir() and os.access(path, os.R_OK):
            for subpath in path.iterdir():
                self._explore(subpath, perm_dict)
    
    def get_perm_dict(self) -> dict[Path, int]:
        perm_dict = {}
        self._explore(self.root_dir, perm_dict)
        return perm_dict
    

def perm_export(src_dir: Path, save_file: Path):
    perm_dict = Exploration(src_dir).get_perm_dict()
    with open(save_file, mode='wb') as file:
        pickle.dump(perm_dict, file)


class PermPatch:
    def __init__(self):
        self.fullpaths: list[Path] = []
        self.st_modes: list[int] = []
    
    def __len__(self) -> int:
        return len(self.fullpaths)
    
    def append(self, p: Path, m: int):
        self.fullpaths.append(p)
        self.st_modes.append(m)
    
    def __repr__(self) -> str:
        rows = []
        for p, new_m in zip(self.fullpaths, self.st_modes):
            old_m = os.stat(p).st_mode
            rows.append(f'[{filemode(old_m)}] -> [{filemode(new_m)}] {str(p)}')
        return '\n'.join(rows)
    
    def apply(self):
        for p, new_m in zip(self.fullpaths, self.st_modes):
            p.lchmod(new_m)
            

def perm_import(dst_dir: Path, save_file: Path) -> PermPatch:
    current_perms = Exploration(dst_dir).get_perm_dict()
    with open(save_file, mode='rb') as file:
        imported_perms = pickle.load(file)
    
    patch = PermPatch()
    for path in current_perms.keys() & imported_perms.keys():
        fullpath = dst_dir.joinpath(path)
        new_st_mode = imported_perms[path]
        old_st_mode = os.stat(fullpath).st_mode
        if new_st_mode != old_st_mode:
            patch.append(fullpath, new_st_mode)
    
    return patch
