"""
Setup a new compendium folder
"""

import subprocess
from argparse import ArgumentParser, Namespace
from pathlib import Path

import logging


def AbsolutePath(*args, **kargs):
    return Path(*args, **kargs).absolute()


def add_subparser(subparsers):
    parser = subparsers.add_parser('init', help=__doc__)
    parser.add_argument("folder", nargs="?", type=AbsolutePath,
                        help="Name of the compendium folder (. or omit to use current folder)")
    parser.add_argument("--python-env", nargs="?", type=AbsolutePath,
                        help="Create a python virtual environment (specify name or usef default 'env')")


def run(args: Namespace):
    get_interactive_arguments(args)
    if args.folder.exists():
        logging.info(f"Using compendium folder at {args.folder}")
    else:
        logging.info(f"Creating compendium folder at {args.folder}")
        args.folder.mkdir()

    if getattr(args, 'create_data', False):
        data = args.folder/"data"
        folders = ["raw"]
        if args.private:
            folders += ["raw-private"]
        if getattr(args, 'encrypt', False):
            folders += ["raw-private-encrypted"]
        logging.info(f"Creating data folders {data}/{folders}")
        data.mkdir()
        for folder in folders:
            (data/folder).mkdir()

    if getattr(args, 'python_env', False) and not args.python_env.exists():
        logging.info(f"Creating Python virtual environment at {args.python_env}")
        cmd = f"python3 -m venv {args.python_env}"
        logging.debug(cmd)
        subprocess.check_call(cmd, shell=True)
        logging.debug("Installing compendium-dodo to virtual environment")
        cmd = f"{args.python_env}/bin/pip install compendium-dodo"
        logging.debug(cmd)
        subprocess.check_call(cmd, shell=True)


def yesno(prompt, default:bool=None, add_options=True):
    if add_options:
        if default is None:
            extra = "[y/n]"
        elif default:
            extra = "[Y/n]"
        else:
            extra = "[y/N]"
        prompt = f"{prompt} {extra}"

    result = input(prompt).lower().strip()
    if (not result) and (default is not None):
        return default
    if result.startswith("y"):
        return True
    if result.startswith("n"):
        return False
    return yesno(prompt, default, add_options=False)


def find_env(location: Path):
    for name in "env", "venv":
        path = location/name
        if (path/"pyvenv.cfg").exists():
            return path


def get_interactive_arguments(args: Namespace):
    if not args.folder:
        folder = input("Name of the compendium (or leave empty to use current folder): ").strip()
        if folder in ("", "."):
            args.folder = Path.cwd()
        else:
            args.folder = Path(folder).absolute()

    # Data and source folders
    data = args.folder/"data"
    if data.exists():
        print(f"Data folder exists at {data}, skipping data folder creation")
    else:
        args.create_data = yesno(f"Create the data folder at {data}?", default=True)
        if args.create_data:
            args.private = yesno(f"Does the project contain private data (i.e. data that cannot be shared)?", default=False)
            if args.private:
                args.encrypt = yesno("Can (some of) the private data be shared in encrypted form?", default=True)

    # Python environment
    if not args.python_env:
        env = find_env(args.folder)
        if env and yesno(f"Use the virtual environment at {env}?", default=True):
            args.pythone_env = env  # use the python env
        elif yesno("Create a python virtual environment?", default=True):
            env = input("Name of the folder (or leave empty to use 'env'): ").strip()
            args.python_env = args.folder/(env or "env")
