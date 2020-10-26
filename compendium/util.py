import logging
import re
import subprocess
from pathlib import Path
from typing import List, Iterable, Tuple


def get_files(folder: Path, suffix=None) -> List[Path]:
    """Get all files contained in Path (optionally filtering for suffix)"""
    if isinstance(suffix, str):
        suffix = [suffix]
    path = Path.cwd() / folder
    if not path.is_dir():
        logging.warning(f"{path} does not exist or is not a directory")
        return []
    return [f for f in path.iterdir() if (f.is_file() and ((suffix is None) or (f.suffix in suffix)))]


def contained_in(parent: Path, descendant: Path) -> bool:
    """Is the second path actually a descendant of the first?"""
    if parent.is_absolute():
        descendant = descendant.absolute()
    return str(descendant.absolute()).startswith(f"{parent}{os.path.sep}")


def get_headers(file: Path) -> Iterable[Tuple[str, str]]:
    """Get [#! command] and [#key: value] headers from a file"""
    for i, line in enumerate(file.open()):
        if not line.strip():
            continue
        if not line.startswith("#"):
            break
        if i == 0 and line.startswith("#!"):
            yield "COMMAND", line[2:].strip()
        m = re.match(r"#(\w+?):(.*)", line)
        if m:
            yield m.groups()[0].strip(), m.groups()[1].strip()


def parse_files(text: str) -> List[Path]:
    """Convert comma-delimited filenames to a list of Path objects"""
    if not text or not text.strip():
        return []
    return [Path(x.strip()) for x in re.split("[ ,]+", text)]


def AbsolutePath(*args, **kargs) -> Path:
    """Create an absolute path (useful as argument 'type')"""
    return Path(*args, **kargs).absolute()


def yesno(prompt, default: bool = None, add_options=True) -> bool:
    """Input prompt, default, and validation for Y/N questions"""
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


def call(cmd: str):
    """Print and call a system command"""
    logging.debug(cmd)
    subprocess.check_call(cmd, shell=True)