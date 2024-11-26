#!/bin/env python3
from __future__ import annotations
from typing import Callable

import argparse
import pathlib

import perms_tools

def confirm_action(confirmation_message, cancelation_message, action):
    if input(f'{confirmation_message} [y/n] ').lower() in ('o', 'y'):
        action()
    else:
        print(cancelation_message)


# ---- commands definitions
def command_export(args):
    perms_tools.perm_export(args.src_directory, args.permission_save_file)


def command_import(args):
    patch = perms_tools.perm_import(args.dst_directory, args.permission_save_file)
    print(patch)
    confirm_action("Proceed ?", "nothing done", lambda: patch.apply())


def command_auto(args):
    patch = perms_tools.perm_auto_patch(args.directory)
    print(patch)
    confirm_action("Proceed ?", "nothing done", lambda: patch.apply())


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


# permcp export [-h] src_directory permission_save_file
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
parser_export.set_defaults(command=command_export)


# permcp import [-h] dst_directory permission_save_file
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
parser_import.set_defaults(command=command_import)


# permcp auto [-h] directory
parser_auto = subparsers.add_parser(
    'auto',
    help="Automatically determines and applies new permissions to a directory"
)
parser_auto.add_argument(
    'directory',
    type=path_checker(is_directory, lambda s: f'Directory not found "{s}"'),
    help="Directory whose permissions will be changed",
    nargs='?',
    default=pathlib.Path()
)
parser_auto.set_defaults(command=command_auto)

args = parser.parse_args()
args.command(args)
