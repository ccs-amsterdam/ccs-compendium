import logging
import subprocess
from argparse import ArgumentParser, Namespace

#from compendium.command.init import find_env
from pathlib import Path

from compendium.initsegment.segment import Segment
from compendium.util import AbsolutePath, yesno, call


class PyEnvSegment(Segment):
    ARGS = ["python_env"]

    @classmethod
    def add_arguments(cls, parser: ArgumentParser):
        parser.add_argument("--python-env", nargs="?", type=AbsolutePath, const='env',
                            help="Create a python virtual environment (specify name or usef default 'env')")

    def run(self, args: Namespace):
        if not args.python_env:
            return
        self.compendium.pyenv = args.python_env
        if not args.python_env.exists():
            install_pyvenv(args.python_env)

    def interactive_arguments(self, args: Namespace):
        if not args.python_env:
            if self.compendium.pyenv:
                args.python_env = self.compendium.pyenv
            else:
                env = find_env(self.compendium.root)
                if env and yesno(f"Use the virtual environment at {env}?", default=True):
                    args.python_env = env  # use the python env
                elif yesno("Create a python virtual environment?", default=True):
                    env = input("Name of the folder (leave empty to use 'env'): ").strip()
                    args.python_env = self.compendium.root / (env or "env")


def find_env(location: Path):
    for name in "env", "venv":
        path = location/name
        if (path/"pyvenv.cfg").exists():
            return path


def install_pyvenv(env: Path):
    logging.info(f"Creating Python virtual environment at {env}")
    call(f"python3 -m venv {env}")
    logging.debug("Installing compendium-dodo to virtual environment")
    call(f"{env}/bin/pip install -U pip wheel")
    call(f"{env}/bin/pip install compendium-dodo")
    setup = env.parent/"setup.py"
    if setup.exists():
        call(f"{env}/bin/pip install -e {setup.parent}")
    req = env.parent/"requirements.txt"
    if req.exists():
        call(f"{env}/bin/pip install -r {req}")
