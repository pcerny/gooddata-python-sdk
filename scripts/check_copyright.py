#!/usr/bin/env python3
# (C) 2022 GoodData Corporation
from __future__ import annotations

import argparse
import fileinput
import re
from datetime import date
from pathlib import Path
from typing import AnyStr

COPYRIGHT_RE: re.Pattern[AnyStr] = re.compile(r"GoodData Corporation", re.IGNORECASE)


def load_ignore_file(ignore_path: Path, verbose: bool) -> list[str]:
    if not ignore_path.exists() or not ignore_path.is_file():
        print(f"Ignore file {str(ignore_path)} not found")
        return []

    with open(ignore_path, "rt") as f:
        ignore_lines = f.readlines()

    result = [line.strip() for line in ignore_lines if not line.startswith("#") and len(line.strip())]
    if verbose:
        print(f"Ignore file {str(ignore_path)} loaded: {str(len(result))} records")
    return result


def comment_copyright(suffix: str, copy_right: str) -> str:
    lower_suffix = suffix.lower()

    if lower_suffix == ".sql":
        return f"-- {copy_right}"
    elif suffix == ".xml":
        return f"<!-- {copy_right} -->"
    else:
        return f"# {copy_right}"


def add_copyright(file_name: Path, insert_line: int) -> None:
    today = date.today()
    file_size = file_name.stat().st_size
    if file_size < 1:
        with open(file_name, "wt", encoding="utf-8") as f:
            f.write(comment_copyright(file_name.suffix, f"(C) {str(today.year)} GoodData Corporation"))
            f.write("\n")
    else:
        with fileinput.input(file_name, inplace=1) as f:
            for pos, line in enumerate(f):
                if pos == insert_line:
                    print(comment_copyright(file_name.suffix, f"(C) {str(today.year)} GoodData Corporation"))
                print(line, end="")


def check_file(file_name: Path, update_file: bool, verbose: bool) -> int:
    if not file_name.is_file():
        print(f"{str(file_name)}: not a file...skipping")
        return 0

    # CONSIDER: introduce mimetypes library to recognize binary files and to select comment character
    insert_line = 1
    with open(file_name, "rt") as f:
        line = f.readline()
        if line.startswith("#!"):
            insert_line = 2
            line = f.readline()

    match = COPYRIGHT_RE.search(line)
    if match:
        if verbose:
            print(f"{str(file_name)}: OK")
        return 0
    else:
        if update_file:
            add_copyright(file_name, insert_line - 1)
            print(f"{str(file_name)}: copyright added")
        else:
            print(f"{str(file_name)}: no copyright")

    return 1


def safe_check_file(file_name: Path, update_file: bool, verbose: bool) -> int:
    try:
        return check_file(file_name, update_file, verbose)
    except Exception as e:
        print(f"{str(file_name)}: unable to process, reason: {str(e)}")
        return 1


def is_ignored_file(ignore_list: list[str], file_name: Path) -> bool:
    for ignore_item in ignore_list:
        if file_name.match(ignore_item):
            return True

    return False


def process_files(file_names: list[str], ignore_list: list[str], update_file: bool, verbose: bool) -> int:
    ret_val = 0
    for file_name in file_names:
        file_path = Path(file_name)
        if not is_ignored_file(ignore_list, file_path):
            ret_val |= safe_check_file(file_path, update_file, verbose)

    return ret_val


def process_folder(folder_path: Path, ignore_list: list[str], update_file: bool, verbose: bool) -> int:
    if not folder_path.is_dir():
        print(f"{str(folder_path)} is not directory")
        return 1

    ret_val = 0
    for object_path in folder_path.glob("*"):
        if not is_ignored_file(ignore_list, object_path):
            if object_path.is_dir():
                ret_val |= process_folder(object_path, ignore_list, update_file, verbose)
            elif object_path.is_file():
                ret_val |= safe_check_file(object_path, update_file, verbose)

    return ret_val


def parse_arguments():
    parser = argparse.ArgumentParser(
        conflict_handler="resolve",
        description="Check and optionally add copyright to selected files",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--ignore",
        default=".copyrightignore",
        help="Path to the file with description what should be excluded from copyright check",
    )
    parser.add_argument("--update", action="store_true", default=False, help="Update file(s) with copyright")
    parser.add_argument(
        "--verbose", action="store_true", default=False, help="Print more detailed information about copyright scan"
    )

    subparsers = parser.add_subparsers(dest="tool_mode", help="tool mode", required=True)
    files_parser = subparsers.add_parser("FILES", help="Accept files to check for copyright")
    files_parser.add_argument("file_names", nargs="*", help="One or more files to check for copyright")

    all_parser = subparsers.add_parser("FOLDER", help="Scan folder for the files to check for copyright")
    all_parser.add_argument("--folder", action="store", default=".", help="Path to the folder to scan")

    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    ignore_list = load_ignore_file(Path(args.ignore), args.verbose)
    if args.tool_mode == "FILES":
        ret_val = process_files(args.file_names, ignore_list, args.update, args.verbose)
    elif args.tool_mode == "FOLDER":
        ret_val = process_folder(Path(args.folder), ignore_list, args.update, args.verbose)
    else:
        print(f"Mode {args.tool_mode} not implemented")
        ret_val = 1

    return ret_val


if __name__ == "__main__":
    exit(main())
