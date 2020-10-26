"""
Encrypt files in the raw-private folder to raw-private-encrypted
"""

import logging
import sys
from argparse import Namespace
from getpass import getpass
from pathlib import Path
from typing import Optional, Iterable


from compendium.command.command import CompendiumCommand
from compendium.compendium import Compendium
from compendium.encryption import encrypt_file, verify_file, get_key


class Encrypt(CompendiumCommand):
    """Encrypt files from private-raw to private-raw-encrypted"""

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("files", nargs="*",
                            help="Specify the files to be encryped (default=all private files)")
        parser.add_argument("--password",
                            help="Specify the password")
        parser.add_argument("--verify", action="store_true",
                            help="Test whether all files are correctly encrypted with this password")

    @classmethod
    def do_run(cls, compendium: Compendium, args: Namespace):
        def _l(f: Path) -> Path:
            return f.relative_to(compendium.root)
        if args.verify:
            for file in compendium.folders.DATA_ENCRYPTED.glob("*"):
                infile = compendium.folders.DATA_PRIVATE/file.name
                if not infile.exists():
                    logging.warning(f"WARNING: Encrypted file {_l(file)} "
                                    f"has no corresponding file in {_l(compendium.PRIVATE)}")

        files = list(get_files(compendium.folders.DATA_PRIVATE, args.files))
        if not files:
            print("No files to encrypt, exiting", file=sys.stderr)
            sys.exit(1)
        if not args.password:
            args.password = getpass("Please specify the password to use: ").strip()
        if not args.password:
            print("No password given, aborting", file=sys.stderr)
            sys.exit(1)
        if not compendium.folders.DATA_ENCRYPTED.exists():
            logging.debug(f"Creating {compendium.folders.DATA_ENCRYPTED}")
            compendium.folders.DATA_ENCRYPTED.mkdir()
        key = get_key(compendium.salt, args.password)
        action = 'Encrypting' if not args.verify else 'Verifying'
        logging.info(f"{action} {len(files)} file(s) from {_l(compendium.folders.DATA_PRIVATE)}")
        for file in files:
            outfile = compendium.folders.DATA_ENCRYPTED/file.name
            if args.verify:
                logging.debug(f".. {_l(outfile)} -> {_l(file)}?")
                if not outfile.exists():
                    print(f"WARNING: File {_l(outfile)} does not exist")
                elif not verify_file(key, file, outfile):
                    print(f"WARNING: File {_l(file)} could not be decrypted from {_l(outfile)}", file=sys.stderr)
            else:
                logging.debug(f".. {file} -> {outfile}")
                encrypt_file(key, file, outfile)


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