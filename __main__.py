#!/bin/env python3
import argparse
import pathlib
import sys

import perms_tools

def confirm_action(confirmation_message, cancelation_message, action):
    if input(f'{confirmation_message} [y/n] ').lower() in ('o', 'y'):
        action()
    else:
        print(cancelation_message)


# ---- commands definitions
def command_export(args):
    save_file = pathlib.Path(args.permission_save_file)
    if save_file.exists():
        sys.exit(f"Save file already exists: {str(save_file)}")

    src = pathlib.Path(args.src_directory)
    if not src.is_dir():
        sys.exit(f"Directory not found: {str(src)}")

    perms_tools.perm_export(src, save_file)


def command_import(args):
    save_file = pathlib.Path(args.permission_save_file)
    if not save_file.is_file():
        sys.exit(f"Save file not found: {str(save_file)}")

    dst = pathlib.Path(args.dst_directory)
    if not dst.is_dir():
        sys.exit(f"Directory not found: {str(dst)}")

    patch = perms_tools.perm_import(dst, save_file)
    print(patch)
    confirm_action("Proceed ?", "nothing done", lambda: patch.apply())


def command_auto(args): #TODO: tester la commande "auto"
    directory = pathlib.Path(args.directory)
    if not directory.is_dir():
        sys.exit(f"Directory not found: {str(directory)}")
    
    patch = perms_tools.perm_auto_patch(directory)
    print(patch)
    confirm_action("Proceed ?", "nothing done", lambda: patch.apply())


# ---- argument parsing
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(required=True)


# permcp export [-h] src_directory permission_save_file
parser_export = subparsers.add_parser(
    'export',
    help="Copies the permissions of a directory into a pickle file"
)
parser_export.add_argument(
    'src_directory',
    type=str,
    help="Directory whose permissions will be copied into `permission_save_file`"
)
parser_export.add_argument(
    'permission_save_file',
    type=str,
    help="Pickle file into which `src_directory` permissions will be exported"
)
parser_export.set_defaults(command=command_export)


# permcp import [-h] dst_directory permission_save_file
parser_import = subparsers.add_parser(
    'import',
    help="Applies to a directory the permissions saved into a pickle file"
)
parser_import.add_argument(
    'dst_directory',
    type=str,
    help="Directory whose permissions will be changed"
)
parser_import.add_argument(
    'permission_save_file',
    type=str,
    help="Pickle file containing the permissions to import into `dst_directory`"
)
parser_import.set_defaults(command=command_import)


# permcp auto [-h] directory
parser_auto = subparsers.add_parser(
    'auto',
    help="Automatically determines and applies new permissions to a directory"
)
parser_auto.add_argument(
    'directory',
    type=str,
    help="Directory whose permissions will be changed"
)
parser_auto.set_defaults(command=command_auto)

args = parser.parse_args()
args.command(args)
