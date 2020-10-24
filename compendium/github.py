import subprocess
import sys
import re
from argparse import ArgumentParser, Namespace
from pathlib import Path

import requests
import logging

from compendium.segment import Segment, yesno, AbsolutePath


def check_github(repository: str) -> str:
    """Check if the repository is valid and exists, returning full URL"""
    if not repository.startswith("https://"):
        if not re.match(r"\w+/\w+", repository):
            raise ValueError("Invalid repository name, format should be full repository URL or userame/repository")
        repository = f"https://github.com/{repository}"
    resp = requests.head(repository)
    if resp.status_code != 200:
        raise ValueError(
            f"Repository does not exist or access denied (url: {repository}, status: {resp.status_code}")
    return repository


def github_folder_name(repository: str) -> str:
    print(repository)
    name = repository.rsplit("/", maxsplit=1)[-1]
    if name.endswith(".git"):
        name = name[:-len(".git")]
    return name


def get_github_name():
    while True:
        name = input(
            "Name of an existing github repository to link to (url or username/repository, leave empty to cancel): ").strip()
        if not name:
            return
        try:
            return check_github(name)
        except ValueError as e:
            print(str(e), file=sys.stderr)
            continue


class GithubSegment(Segment):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("folder", nargs="?", type=AbsolutePath,
                        help="Name of the compendium folder (. for current folder, omit to use github folder)")
        parser.add_argument("--github",
                        help="Link compendium to github repository (URL or username/repository)")

    def check_arguments(self, args: Namespace):
        for arg in 'github', 'folder':
            if not hasattr(args, arg):
                setattr(args, arg, None)
        if not hasattr(args, 'folder'):
            args.folder = None
        if args.github and not check_github(args.github):
            raise ValueError(f"Github repository invalid: {args.github}")

    def interactive_arguments(self, args: Namespace):
        # check if project folder has .git, in that case use it and ignore github flag
        if args.folder:
            if (args.folder / ".git").exists():
                if args.github:
                    logging.info(f"Compendium folder {args.folder} is already git repository, so ignoring github link")
                    args.github = None
                return
        elif (Path.cwd()/".git").exists():
            if yesno(f"Current folder {Path.cwd()} is a git repository, use it as the project folder?", default=True):
                args.folder = Path.cwd()
                args.github = None
                return

        # Check whether user wants to use github
        if (not args.github) and yesno("Link the compendium to a github repository?", default=True):
            print("Note: If you haven't created a repository yet, you can do so now at https://github.com/new")
            args.github = get_github_name()
        if args.folder and args.github:
            if args.folder.name != github_folder_name(args.github):
                if not yesno(f"Folder name {args.folder.name} does not match "
                             f"github repository name {github_folder_name(args.github)}, "
                             f"are you sure you want to proceed", default=True):
                    print("Aborted", file=sys.stderr)
                    sys.exit(1)

        # Determine folder name if needed
        if not args.folder:
            if args.github:
                repo = Path.cwd()/github_folder_name(args.github)

                question = (f"Use existing folder {repo}?" if repo.exists()
                            else f"Clone github repository into new folder {repo}?")
                if yesno(question, default=True):
                    args.folder = repo
                if (repo/".git").exists():
                    logging.info(f"Folder {repo} is already a git repository, so ignoring github link")
                    args.github = None
        if not args.folder:
            if yesno(f"Use current folder {Path.cwd()}?", default=True):
                args.folder = Path.cwd()
            else:
                name = input("Name of the folder to use (will be created if needed, omit to cancel): ")
                if name:
                    args.folder = Path.cwd()/name
                else:
                    print("Aborted", file=sys.stderr)
                    sys.exit(1)

    def run(self, args: Namespace):
        if args.github:
            if not args.github.startswith("https://"):
                args.github = f"https://github.com/{args.github}"
            if args.folder.exists():
                if (args.folder/".git").exists():
                    logging.warning(f"Folder {args.folder} is already a git repository, ignoring github link")
                logging.info(f"Linking {args.folder} to github repository {args.github}")
                subprocess.check_call("git init", shell=True, cwd=args.folder)
                subprocess.check_call(f"git remote add origin {args.github}", shell=True, cwd=args.folder)
                subprocess.check_call("git fetch", shell=True, cwd=args.folder)
                subprocess.check_call("git checkout --track origin/main", shell=True, cwd=args.folder)
            else:
                logging.info(f"Cloning {args.github} to new folder {args.folder}")
                subprocess.check_call(f"git clone {args.github} {args.folder}", shell=True)

        else:
            if args.folder.exists():
                logging.info(f"Using compendium folder at {args.folder}")
            else:
                logging.info(f"Creating compendium folder at {args.folder}")
                args.folder.mkdir()

