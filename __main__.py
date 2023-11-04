#!/bin/env python3
import argparse
import pathlib
import sys

import permtools

# ---- commands definitions
def command_export(args):
    save_file = pathlib.Path(args.permission_save_file)
    if save_file.exists():
        sys.exit(f"Save file already exists: {str(save_file)}")

    src = pathlib.Path(args.src_directory)
    if not src.is_dir():
        sys.exit(f"Directory not found: {str(src)}")

    permtools.perm_export(src, save_file)


def command_import(args):
    save_file = pathlib.Path(args.permission_save_file)
    if not save_file.is_file():
        sys.exit(f"Save file not found: {str(save_file)}")

    dst = pathlib.Path(args.dst_directory)
    if not dst.is_dir():
        sys.exit(f"Directory not found: {str(dst)}")

    patch = permtools.perm_import(dst, save_file)

    print(patch)
    confirmation = input("Proceed ? [y/n] ")
    if confirmation.lower() not in ('o', 'y'):
        print("nothing done")
        sys.exit()

    patch.apply()


# ---- argument parsing
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(required=True)


# permcp export [-h] src_directory permission_save_file
parser_export = subparsers.add_parser(
    'export',
    help="Copies the permissions of a directory into a pickle file."
)
parser_export.add_argument(
    'src_directory',
    type=str,
    help="Directory whose permissions will be copied into `permission_save_file`."
)
parser_export.add_argument(
    'permission_save_file',
    type=str,
    help="Pickle file into which `src_directory` permissions will be exported."
)
parser_export.set_defaults(command=command_export)


# permcp import [-h] dst_directory permission_save_file
parser_import = subparsers.add_parser(
    'import',
    help="Applies to a directory the permissions saved into a pickle file."
)
parser_import.add_argument(
    'dst_directory',
    type=str,
    help="Directory whose permissions will be changed."
)
parser_import.add_argument(
    'permission_save_file',
    type=str,
    help="Pickle file containing the permissions to import into `dst_directory`."
)
parser_import.set_defaults(command=command_import)


args = parser.parse_args()
args.command(args)
