"""
Setup a new compendium folder
"""
import re
import subprocess
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

import logging
from urllib.request import urlretrieve

import requests

from compendium.segment import AbsolutePath, Segment, yesno


def add_subparser(subparsers):
    parser = subparsers.add_parser('init', help=__doc__)
    for segment in get_segments():
        segment.add_arguments(parser)


def run(args: Namespace):
    for segment in get_segments():
        try:
            segment.check_arguments(args)
        except Exception as e:
            print(f"Invalid argument: {e}", file=sys.stderr)
    for segment in get_segments():
        segment.interactive_arguments(args)
        segment.run(args)





def find_env(location: Path):
    for name in "env", "venv":
        path = location/name
        if (path/"pyvenv.cfg").exists():
            return path


class PyEnvSegment(Segment):
    ARGS = ["python_env"]

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("--python-env", nargs="?", type=AbsolutePath,
                            help="Create a python virtual environment (specify name or usef default 'env')")

    def run(self, args: Namespace):
        if args.python_env and not args.python_env.exists():
            logging.info(f"Creating Python virtual environment at {args.python_env}")
            cmd = f"python3 -m venv {args.python_env}"
            logging.debug(cmd)
            subprocess.check_call(cmd, shell=True)
            logging.debug("Installing compendium-dodo to virtual environment")
            cmd = f"{args.python_env}/bin/pip install -U pip wheel"
            logging.debug(cmd)
            subprocess.check_call(cmd, shell=True)
            cmd = f"{args.python_env}/bin/pip install compendium-dodo"
            logging.debug(cmd)
            subprocess.check_call(cmd, shell=True)

    def interactive_arguments(self, args: Namespace):
        if not args.python_env:
            env = find_env(args.folder)
            if env and yesno(f"Use the virtual environment at {env}?", default=True):
                args.pythone_env = env  # use the python env
            elif yesno("Create a python virtual environment?", default=True):
                env = input("Name of the folder (or leave empty to use 'env'): ").strip()
                args.python_env = args.folder / (env or "env")

def get_segments():
    from compendium.check import CheckSegment
    from compendium.folderstructure import FolderStructureSegment
    from compendium.github import GithubSegment
    return [
        GithubSegment(),
        FolderStructureSegment(),
        PyEnvSegment(),
        CheckSegment(),
    ]