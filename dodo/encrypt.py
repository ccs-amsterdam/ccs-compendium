"""
Encrypt files in the raw-private folder to raw-private-encrypted
"""

import base64
import logging
import sys
from argparse import Namespace
from configparser import ConfigParser
from getpass import getpass
from pathlib import Path
from typing import Optional, Iterable

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def add_subparser(subparsers):
    parser = subparsers.add_parser('encrypt', help=__doc__)
    parser.add_argument("files", nargs="*",
                        help="Specify the files to be encryped (default=all private files)")
    parser.add_argument("--password",
                        help="Specify the password")
    parser.add_argument("--folder", type=Path,
                        help="Compendium folder (if not current folder")
    parser.add_argument("--verify", action="store_true",
                        help="Test whether all files are correctly encrypted with this password")


def get_root(folder: Optional[Path]):
    if folder is None:
        folder = Path.cwd()
    folders = [folder] + list(folder.absolute().parents)
    for folder in folders:
        if (folder / ".dodo.cfg").exists():
            logging.debug(f"Using compendium folder at {folder}")
            return folder
    raise FileNotFoundError(f"Could not find compendium folder, looked for .dodo.cfg in {folders}")


def get_config(folder: Path):
    cf = ConfigParser()
    cf.read(folder/".dodo.cfg")
    return cf


def get_key(cfg: ConfigParser, password: bytes) -> bytes:
    # From: https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/#nist
    salt = cfg.get(section="encryption", option="salt").encode('utf-8')
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000
    )
    return base64.urlsafe_b64encode(kdf.derive(password))


def get_files(folder: Path, files: Optional[Iterable[str]]):
    if not files:
        yield from folder.glob("*")
    else:
        for file in files:
            if file.startswith("/"):  # absolute path
                file = Path(file)
            elif "/" in file: # relative wrt current folder
                file = Path.cwd()/file
            else:  # relative wrt private data folder
                file = folder/file
            if file.parent != folder:
                raise Exception(f"Cannot encrypt {file}, not in {folder}")
            yield file


def do_verify(key: bytes, infile: Path, outfile: Path):
    fernet = Fernet(key)
    with infile.open('rb') as f:
        plaintext = f.read()
    with outfile.open('rb') as f:
        ciphertext = f.read()
    decrypted = fernet.decrypt(ciphertext)
    return decrypted == plaintext


def do_encrypt(key: bytes, infile: Path, outfile: Path):
    fernet = Fernet(key)
    with infile.open('rb') as f:
        data = f.read()
    with outfile.open('wb') as f:
        f.write(fernet.encrypt(data))


def run(args: Namespace):
    root = get_root(args.folder)

    def _l(p: Path):
        return p.relative_to(root)
    cfg = get_config(root)
    infolder = root/"data"/"raw-private"
    outfolder = root/"data"/"raw-private-encrypted"
    if args.verify:
        for file in outfolder.glob("*"):
            infile = infolder / file.name
            if not infile.exists():
                print(f"WARNING: Encrypted file {_l(file)} has not corresponding file in {_l(infolder)}", file=sys.stderr)

    files = list(get_files(infolder, args.files))
    if not files:
        print("No files to encrypt, exiting", file=sys.stderr)
        sys.exit(1)
    if not args.password:
        args.password = getpass("Please specify the password to use: ").strip()
    if not args.password:
        print("No password given, aborting", file=sys.stderr)
        sys.exit(1)

    key = get_key(cfg, args.password.encode('utf-8'))
    logging.info(f"{'Encrypting' if not args.verify else 'Verifying'} {len(files)} file{'s' if len(files)>1 else ''} from {_l(infolder)}")
    for file in files:
        outfile = outfolder/file.name
        if args.verify:
            logging.debug(f".. {_l(outfile)} -> {_l(file)}?")
            if not outfile.exists():
                print(f"WARNING: File {_l(outfile)} does not exist")
            elif not do_verify(key, file, outfile):
                print(f"WARNING: File {_l(file)} could not be decrypted from {_l(outfile)}", file=sys.stderr)
        else:
            logging.debug(f".. {file} -> {outfile}")
            do_encrypt(key, file, outfile)