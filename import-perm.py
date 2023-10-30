#!/bin/env python3
import pathlib
import argparse
import sys

from perm import perm_import

parser = argparse.ArgumentParser()
parser.add_argument('dst_directory', type=str,
    help="Destination directory in which the imported permissions will be applied"
)
parser.add_argument('permission_save_file', type=str,
    help="Pickle file that contains the permissions to import"
)
args = parser.parse_args()

save_file = pathlib.Path(args.permission_save_file)
if not save_file.is_file():
    sys.exit(f"Save file not found: {str(save_file)}")

dst = pathlib.Path(args.dst_directory)
if not dst.is_dir():
    sys.exit(f"Directory not found: {str(dst)}")

patch = perm_import(dst, save_file)

print(patch)
confirmation = input("Proceed ? [y/n] ")
if confirmation.lower() not in ('o', 'y'):
    print("nothing done")
    sys.exit()

patch.apply()
