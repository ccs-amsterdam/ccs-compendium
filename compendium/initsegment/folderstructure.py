import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path
from urllib.request import urlretrieve

from compendium.initsegment.segment import Segment
from compendium.util import yesno


def _download(fn: str, dest: Path):
    dest.parent.mkdir(exist_ok=True)
    url = f"https://raw.githubusercontent.com/vanatteveldt/compendium-dodo/main/templates/{fn}"
    logging.info(f"Downloading {url} to {dest}")
    urlretrieve(url, dest)


class FolderStructureSegment(Segment):
    ARGS=["dodofile", "gitignore", "license", "data"]

    @classmethod
    def add_arguments(cls, parser: ArgumentParser):
        parser.add_argument("--dodofile", nargs="?", const="yes", choices=["yes", "no"],
                            help="Download the template dodo.py file? ")
        parser.add_argument("--gitignore", nargs="?", const="yes", choices=["yes", "no"],
                            help="Download the template .gitignore file?")
        parser.add_argument("--license", choices=["mit", "ccby", "no"],
                            help="Download one of the default license files?")
        parser.add_argument("--create-data", nargs="?", choices=["yes", "private", "encrypted", "no"],
                            help="Create the data folders?", dest="data")
        parser.add_argument("--create-src", nargs="?", choices=["yes",  "no"], const="yes",
                            help="Create source folders?", dest="src")
        parser.add_argument("--example-files", nargs="?", choices=["yes",  "no"], const="yes",
                            help="Download example compendium files?", dest="examplefiles")

    def interactive_arguments(self, args: Namespace):
        data = args.folder / "data"
        if data.exists():
            logging.debug(f"Data folder exists at {data}, skipping data folder creation questions")
        else:
            if not yesno(f"Create the data folder at {data}?", default=True):
                args.data = "no"
            elif not yesno(f"Does the project contain private data (i.e. data that cannot be shared)?", default=False):
                args.data = "yes"
            elif yesno("Can (some of) the private data be shared in encrypted form?", default=True):
                args.data = "encrypted"
            else:
                args.data = "private"
            args.src = "yes" if yesno("Create source folders for analysis scripts?", default=True) else "no"
            if "no" not in (args.src, args.data):
                args.examplefiles = "yes" if yesno("Download example files from template?", default=False) else "no"

        def _askdownload(file: Path):
            return (not file.exists()) and yesno(f"Download the template {file.name} file?", default=True)
        if not args.dodofile:
            args.dodofile = "yes" if _askdownload(args.folder / "dodo.py") else "no"
        if not args.gitignore:
            args.gitignore = "yes" if _askdownload(args.folder / ".gitignore") else "no"
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
        if args.data != "no":
            folders = ["", "raw", "intermediate"]
            if args.data in {"private", "encrypted"}:
                folders += ["raw-private"]
            if args.data == "encrypted":
                folders += ["raw-private-encrypted"]
            folders = [f for f in folders if not (data/f).exists()]
            if folders:
                logging.info(f"Creating data folders {data}/{folders}")
                for folder in folders:
                    (data / folder).mkdir()
        if args.src == "yes":
            src = args.folder / "src"
            folders = ["", "data-processing", "analysis"]
            logging.info(f"Creating source folders {src}/{folders}")
            for folder in folders:
                (src / folder).mkdir()
        if args.examplefiles == "yes":
            _download("example.py", self.compendium.folders.SRC_PROCESSING / "example.py")
            _download("example2.py", self.compendium.folders.SRC_PROCESSING / "example2.py")
            _download("secret.txt", self.compendium.folders.DATA_PRIVATE / "secret.txt")
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

    def check(self):
        yield "Data Folders", (self.compendium.root / "data").exists()
        yield "License file", (self.compendium.root / "LICENSE").exists()
        yield "dodo.py file", (self.compendium.root / "dodo.py").exists()



