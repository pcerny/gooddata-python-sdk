#!/usr/bin/env python3
# Copyright 2021 GoodData Corporation


__doc__ = """This script sets the given version to all subcomponents equally.
It does nothing more. You should ensure that you have correct dependencies in
subcomponents (see all setup.py files)"""


import os
import sys

components = [
    "gooddata-sdk",
    "gooddata-metadata-client",
    "gooddata-afm-client",
    "gooddata-scan-client",
    "gooddata-fdw",
    "gooddata-pandas",
]


def write_version(version, component):
    abspath = os.path.abspath(os.path.dirname(__file__))
    with open(f"{abspath}/../{component}/VERSION", "w") as version_file:
        version_file.write(version)


def run(version):
    for component in components:
        write_version(version, component)


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("No version given", file=sys.stderr)
        print(__doc__)
        exit(1)
    else:
        arg1 = sys.argv[1]
        if arg1 in ("help", "--help", "-h"):
            print(__doc__)
        else:
            run(arg1)
