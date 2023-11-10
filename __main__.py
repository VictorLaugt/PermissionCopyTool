#!/bin/env python3
from __future__ import annotations
from typing import Callable

import argparse
import pathlib

import operations

# ---- linking commands
def command_import(args):
    operations.import_perms(args.dst_directory, args.permission_save_file)

def command_export(args):
    operations.export_perms(args.src_directory, args.permission_save_file)

def command_auto(args):
    operations.auto_perms(args.directory)


# ---- argument parsing
PathPredicate = Callable[[pathlib.Path], bool]
ErrorMessageGenerator = Callable[[str], str]

is_directory: PathPredicate = lambda p: p.is_dir()
is_file = lambda p: p.is_file()
do_not_exists = lambda p: not p.exists()
exists = lambda p: p.exists()

def path_checker(predicate: PathPredicate, err_msg_gen: ErrorMessageGenerator):
    def argparse_path_type(arg: str) -> pathlib.Path:
        path = pathlib.Path(arg)
        if predicate(path):
            return path
        raise argparse.ArgumentTypeError(err_msg_gen(arg))
    return argparse_path_type

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(required=True)


# permtool export [-h] src_directory permission_save_file
parser_export = subparsers.add_parser(
    'export',
    help="Copies the permissions of a directory into a pickle file"
)
parser_export.add_argument(
    'src_directory',
    type=path_checker(is_directory, lambda s: f'Directory not found "{s}"'),
    help="Directory whose permissions will be copied into `permission_save_file`"
)
parser_export.add_argument(
    'permission_save_file',
    type=path_checker(do_not_exists, lambda s: f'File already exists "{s}"'),
    help="Pickle file into which `src_directory` permissions will be exported"
)
parser_export.set_defaults(command=operations.export_perms)


# permtool import [-h] dst_directory permission_save_file
parser_import = subparsers.add_parser(
    'import',
    help="Applies to a directory the permissions saved into a pickle file"
)
parser_import.add_argument(
    'dst_directory',
    type=path_checker(is_directory, lambda s: f'Directory not found "{s}"'),
    help="Directory whose permissions will be changed"
)
parser_import.add_argument(
    'permission_save_file',
    type=path_checker(exists, lambda s: f'Save file not found "{s}"'),
    help="Pickle file containing the permissions to import into `dst_directory`"
)
parser_import.set_defaults(command=operations.import_perms)


# permtool auto [-h] directory
parser_auto = subparsers.add_parser(
    'auto',
    help="Automatically determines and applies new permissions to a directory"
)
parser_auto.add_argument(
    'directory',
    type=path_checker(is_directory, lambda s: f'Directory not found "{s}"'),
    help="Directory whose permissions will be changed"
)
parser_auto.set_defaults(command=operations.auto_perms)

args = parser.parse_args()
args.command(args)
