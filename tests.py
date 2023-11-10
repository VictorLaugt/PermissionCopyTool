from __future__ import annotations
from typing import Union, Collection

import unittest

import random
import pathlib
import shutil
import os
import stat

import perms_tools
import operations

class FileStructure:
    @staticmethod
    def random_perm() -> int:
        result = 0
        for perm in (
                stat.S_IRUSR, stat.S_IWUSR, stat.S_IXUSR,
                stat.S_IRGRP, stat.S_IWGRP, stat.S_IXGRP,
                stat.S_IROTH, stat.S_IWOTH, stat.S_IXOTH
                ):
            result |= random.randrange(2) * perm
        return result

    def __init__(self, name, perm = None):
        self.name: str = name
        self.perm: int = perm if perm is not None else self.random_perm()
    
    def build_into(self, dirpath: pathlib.Path) -> None:
        dirpath.joinpath(self.name).touch(self.perm)
    
    def same_perms(self, dirpath: pathlib.Path) -> bool:
        return self.perm == os.stat(dirpath.joinpath(self.name))
    
    def default_perms(self, dirpath: pathlib.Path) -> bool:
        return perms_tools.DEFAULT_FILE_PERMS == os.stat(dirpath.joinpath(self.name))

class DirStructure(FileStructure):
    @classmethod
    def random_perm(cls) -> int:
        return super().random_perm() | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR

    def __init__(self, name, members, perm = None):
        super().__init__(name, perm)
        self.members: Collection[FileStructure] = members
    
    def build_into(self, dirpath: pathlib.Path) -> None:
        subdirpath = dirpath.joinpath(self.name)
        subdirpath.mkdir(self.perm, exist_ok=True)
        for m in self.members:
            m.build_into(subdirpath)
    
    def same_perms(self, dirpath: pathlib.Path) -> bool:
        subdirpath = dirpath.joinpath(self.name)
        print(f"DEBUG: {subdirpath} {stat.filemode(self.perm)}, {stat.filemode(os.stat(subdirpath).st_mode)}")
        return (
            self.perm == os.stat(subdirpath).st_mode and
            all(m.same_perms(subdirpath) for m in self.members)
        )
    
    def default_perms(self, dirpath: pathlib.Path) -> bool:
        subdirpath = dirpath.joinpath(self.name)
        return (
            perms_tools.DEFAULT_DIR_PERMS == os.stat(subdirpath).st_mode and
            all(m.default_perms(subdirpath) for m in self.members)
        )

random_dir_perms = [DirStructure.random_perm() for _ in range(4)]
random_file_perms = [FileStructure.random_perm() for _ in range(4)]

SRC_CONTENT = DirStructure(
    name="Coco",
    perm=random_dir_perms[0],
    members=(
        FileStructure(name="coco.jpg", perm=random_file_perms[0]),
        FileStructure(name="zozo.txt"),  # non présent dans `playground_dst`
        FileStructure(name=".foo.md", perm=random_file_perms[1]),
        DirStructure(
            name="A Name With Spaces",
            perm=random_dir_perms[1],
            members=(FileStructure(name="biloute"),)  # non présent dans `playground_dst`
        ),
        DirStructure(
            name="Toto",
            perm=random_dir_perms[3],
            members=(
                FileStructure(name="dontreadme.md", perm=random_file_perms[2]),
                FileStructure(name="a name with spaces.txt", perm=random_file_perms[3])
            )
        ),
        DirStructure(  # non présent dans `playground_dst`
            name="Bar",
            members=(DirStructure(name="Zoo", members=()),)
        )
    )
)

DST_CONTENT = DirStructure(
    name="Coco",
    perm=random_dir_perms[0],
    members=(
        FileStructure(name="coco.jpg", perm=random_file_perms[0]),
        FileStructure(name="hey.txt"),  # non présent dans `playground_src`
        FileStructure(name=".foo.md", perm=random_file_perms[1]),
        DirStructure(
            name="A Name With Spaces",
            perm=random_dir_perms[1],
            members=(FileStructure(name="trouloulou"),)  # non présent dans `playground_src`
        ),
        DirStructure(
            name="Toto",
            perm=random_dir_perms[3],
            members=(
                FileStructure(name="dontreadme.md", perm=random_file_perms[2]),
                FileStructure(name="a name with spaces.txt", perm=random_file_perms[3])
            )
        )
    )
)

EXCPECTED_PERMS = DirStructure(
    name="Coco",
    perm=random_dir_perms[0],
    members=(
        FileStructure(name="coco.jpg", perm=random_file_perms[0]),
        FileStructure(name=".foo.md", perm=random_file_perms[1]),
        DirStructure(
            name="A Name With Spaces",
            perm=random_dir_perms[1],
            members=()
        ),
        DirStructure(
            name="Toto",
            perm=random_dir_perms[3],
            members=(
                FileStructure(name="dontreadme.md", perm=random_file_perms[2]),
                FileStructure(name="a name with spaces.txt", perm=random_file_perms[3])
            )
        )
    )
)

TEST_DIR = pathlib.Path(__file__).resolve().with_name("Tests")
SRC = TEST_DIR.joinpath("Src")
DST = TEST_DIR.joinpath("Dst")
SAVE_FILE = TEST_DIR.joinpath("coco-save-file.pickle.py")

class Test(unittest.TestCase):            
    def test__import_export(self):
        # initializes test environment
        SRC.mkdir(exist_ok=True)
        DST.mkdir(exist_ok=True)
        SAVE_FILE.unlink(missing_ok=True)
        
        # tests
        SRC_CONTENT.build_into(SRC)
        DST_CONTENT.build_into(DST)
        operations.export_perms(SRC, SAVE_FILE)
        self.assertTrue(SAVE_FILE.is_file())
        operations.import_perms(DST, SAVE_FILE)
        self.assertTrue(EXCPECTED_PERMS.same_perms(DST))
        
        # cleans test environment
        shutil.rmtree(SRC, ignore_errors=True)
        shutil.rmtree(DST, ignore_errors=True)
        SAVE_FILE.unlink(missing_ok=True)

    
    # def test__auto(self):
    #     # initializes test environment
    #     SRC.mkdir(exist_ok=True)
    #     SAVE_FILE.unlink(missing_ok=True)
        
    #     # tests        
    #     SRC_CONTENT.build_into(SRC)
    #     operations.auto_perms(SRC)
    #     self.assertTrue(SRC_CONTENT.default_perms(SRC))
        
    #     # cleans test environment
    #     shutil.rmtree(SRC, ignore_errors=True)
    #     SAVE_FILE.unlink(missing_ok=True)


if __name__ == '__main__':
    unittest.main()
