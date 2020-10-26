import logging
from argparse import Namespace
from configparser import ConfigParser, NoSectionError, NoOptionError
import crypt
from pathlib import Path
from typing import Optional, Iterable

from cryptography.fernet import InvalidToken
from doit.exceptions import TaskFailed

from compendium.action import Action
from compendium.encryption import get_key, decrypt_file
from compendium.util import get_files, get_headers, parse_files, call

CONFIGFILE = ".compendium.cfg"

EXT_SCRIPT = {".py", ".R", ".Rmd", ".sh"}

class Folders:
    def __init__(self, root: Path):
        self.ROOT = root
        self.DATA = data = root/"data"
        self.DATA_PRIVATE = data/"raw-private"
        self.DATA_ENCRYPTED = data/"raw-private-encrypted"
        self.DATA_RAW = data/"raw"
        self.DATA_INTERMEDIATE= data/"intermediate"

        self.SRC = src = root/"src"
        self.SRC_PROCESSING = src/"data-processing"
        self.SRC_ANALYSIS = src/"analysis"


def find_root(folder: Path) -> Path:
    if folder is None:
        raise ValueError("Compendium folder cannot be None")
    for f in [folder] + list(folder.parents):
        if (f / CONFIGFILE).exists():
            return f
    raise FileNotFoundError(f"Cannot find compendium folder (starting from {folder})")


class Compendium:
    def __init__(self, folder: Path = None, create_new_config=False):
        if folder is None:
            folder = Path.cwd()
        self.cf = ConfigParser()
        if create_new_config:
            self.changed = True
            self.root = folder
        else:
            self.changed = False
            self.root = find_root(folder)
            logging.info(f"Reading configuration file {self.root / CONFIGFILE}")
            self.cf.read(self.root / CONFIGFILE)
        self.folders = Folders(self.root)

    # **** Configuration file management ****

    def save(self, force=False):
        if not (force or self.changed):
            return
        config = self.root / CONFIGFILE
        logging.info(f"Writing compendium configuraton to {config}")
        with config.open('w') as f:
            f.write("# Compendium configuration file\n")
            self.cf.write(f)
        self.changed = False

    def set(self, section: str, option: str, value: str):
        if not self.cf.has_section(section):
            self.cf.add_section(section)
        val = self.get(section, option)
        if val != value:
            logging.debug(f"SET [{section}] {option} to {value} (was:{val})")
            self.cf.set(section, option, value)
            self.changed = True

    def get(self, section: str, option: str, default: str = None) -> str:
        return self.cf.get(section, option, fallback=default)

    @property
    def salt(self) -> str:
        salt = self.get(section="encryption", option="salt")
        if not salt:
            salt = crypt.mksalt()
            self.set("encryption", "salt", salt)
        return salt

    @property
    def pyenv(self) -> Path:
        env = self.cf.get("python", "env", fallback=None)
        if env:
            return self.root / env

    @pyenv.setter
    def pyenv(self, env: Path):
        self.set("python", "env", str(env.relative_to(self.root)))

    def _section(self, section: str):
        if not self.cf.has_section(section):
            self.cf.add_section(section)
        return self.cf[section]

    # **** Tasks and actions ****

    def get_actions(self) -> Iterable[Action]:
        """Yield all processing and analysis scripts"""
        files = (get_files(self.folders.SRC_PROCESSING, suffix=EXT_SCRIPT) +
                 get_files(self.folders.SRC_ANALYSIS, suffix=EXT_SCRIPT))
        for file in files:
            headers = dict(get_headers(file))
            if "CREATES" in headers and "COMMAND" in headers:
                targets = parse_files(headers["CREATES"])
                inputs = parse_files(headers.get("DEPENDS"))
                # build action
                action = f"{headers['COMMAND']} {file}"
                if headers.get("PIPE", "F")[0].lower() == "t":
                    if len(inputs) > 1 or len(targets) > 1:
                        raise ValueError("File {file}: Cannot use PIPE with multiple inputs or outputs")
                    if inputs:
                        action = f"{action} < {inputs[0]}"
                    action = f"{action} > {targets[0]}"
                if file.suffix == ".py" and self.pyenv:
                    # Activate virtual environent before calling script
                    action = f"(. {self.pyenv}/bin/activate; {action})"
                action = f'{action} && echo "[OK] {file.name} completed" 1>&2'
                yield Action(file, action, targets, inputs, headers)

    def decrypt_file_task(self, password: str, source: Path, target: Path):
        if password is None:
            return TaskFailed("No passphrase specified; please use doit passphrase=**** decrypt")
        target.parent.mkdir(exist_ok=True)
        key = get_key(self.salt, password)
        try:
            decrypt_file(key, source, target)
        except InvalidToken:
            return TaskFailed("Incorrect password, could not decrypt files")

    def install_python_task(self):
        from compendium.initsegment.pyenv import install_pyvenv
        install_pyvenv(self.pyenv)