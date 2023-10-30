#!/bin/env python3
import pathlib
import argparse
import sys

from perm import perm_export

parser = argparse.ArgumentParser()
parser.add_argument('src_directory', type=str,
    help="Directory whose permissions will be copied into `permission_save_file`."
)
parser.add_argument('permission_save_file', type=str,
    help="Pickle file into which `src_directory` permissions will be exported."
)
args = parser.parse_args()

save_file = pathlib.Path(args.permission_save_file)
if save_file.exists():
    sys.exit(f"Save file already exists: {str(save_file)}")

src = pathlib.Path(args.src_directory)
if not src.is_dir():
    sys.exit(f"Directory not found: {str(src)}")

perm_export(src, save_file)
