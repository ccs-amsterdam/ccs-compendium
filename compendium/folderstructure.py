import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path
from urllib.request import urlretrieve

from compendium.segment import Segment, yesno


def _download(fn: str, dest: Path):
    url = f"https://raw.githubusercontent.com/vanatteveldt/compendium-dodo/main/templates/{fn}"
    logging.info(f"Downloading {url} to {dest}")
    urlretrieve(url, dest)


class FolderStructureSegment(Segment):
    ARGS=["dodofile", "gitignore", "license", "data"]

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("--dodofile", nargs="?", const="yes", choices=["yes", "no"],
                            help="Download the dodo.py file? (download skips if existing, update forces new download)")
        parser.add_argument("--gitignore", nargs="?", const="yes", choices=["yes", "no"],
                            help="Download the default .gitignore file? (download skips if existing, update forces new download)")
        parser.add_argument("--license", choices=["mit", "ccby", "no"],
                            help="Download one of the default license files?")
        parser.add_argument("--create_data", nargs="?", choices=["yes", "private", "encrypted", "no"],
                            help="Creaate the data folders?", dest="data")

    def interactive_arguments(self, args: Namespace):
        data = args.folder / "data"
        if data.exists():
            logging.debug(f"Data folder exists at {data}, skipping data folder creation")
        else:
            if not yesno(f"Create the data folder at {data}?", default=True):
                args.data = "no"
            elif not yesno(f"Does the project contain private data (i.e. data that cannot be shared)?",
                                     default=False):
                args.data = "yes"
            elif yesno("Can (some of) the private data be shared in encrypted form?", default=True):
                args.data = "encrypted"
            else:
                args.data = "private"
        if not args.dodofile:
            f = args.folder / "dodo.py"
            q = yesno(f"{'Update (re-download)' if f.exists() else 'Download'} the template dodo.py file?", default=(not f.exists()))
            args.dodofile = "yes" if q else "no"
        if not args.gitignore:
            f = args.folder / ".gitignore"
            q = yesno(f"{'Update (re-download)' if f.exists() else 'Download'} the template .gitignore file?", default=(not f.exists()))
            args.gitignore = "yes" if q else "no"
        if not args.license:
            if (args.folder / "LICENSE").exists():
                logging.debug("LICENSE file exists, skipping license selection")
            elif yesno("Download a template license file to let others know whether they can reuse your material?",
                       default=True):
                print("We have templates for the MIT and CC-BY licenses.")
                print("For more information, see https://opensource.org/licenses")
                if yesno("Use the MIT license? (great for sharing code with minimal strings attached)",
                         default=True):
                    args.license = "mit"
                elif yesno("Use the CC-BY license? (attribution is required, best for reports and documentation)",
                           default=True):
                    args.license = "ccby"
                else:
                    print("No license selected. Please go to https://opensource.org/licenses ")

    def run(self, args: Namespace):
        data = args.folder / "data"
        if data.exists():
            logging.debug(f"Data folder {data} exists, skipping data folder creation")
        elif args.data != "no":
            folders = ["raw"]
            if args.data in {"private", "encrypted"}:
                folders += ["raw-private"]
            if args.data == "encrypted":
                folders += ["raw-private-encrypted"]
            logging.info(f"Creating data folders {data}/{folders}")
            data.mkdir()
            for folder in folders:
                (data / folder).mkdir()

        if args.dodofile == "yes":
            _download("dodo.py", args.folder / "dodo.py")
        if args.gitignore == "yes":
            _download("gitignore", args.folder / ".gitignore")
        licensefile = args.folder / "LICENSE"
        if not licensefile.exists():
            if args.license == "mit":
                _download("LICENSE-MIT", licensefile)
            if args.license == "ccby":
                _download("LICENSE-CC-BY", licensefile)

    def check(self, args: Namespace):
        yield "Data Folders", (args.folder / "data").exists()
        yield "License file", (args.folder / "LICENSE").exists()
        yield "dodo.py file", (args.folder / "dodo.py").exists()