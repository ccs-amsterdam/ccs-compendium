from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Sequence, Tuple


class Segment:
    ARGS = []

    def add_arguments(self, parser: ArgumentParser):
        pass

    def check_arguments(self, args: Namespace):
        for arg in self.ARGS:
            if not hasattr(args, arg):
                setattr(args, arg, None)

    def interactive_arguments(self, args: Namespace):
        pass

    def run(self, args: Namespace):
        pass

    def check(self, args: Namespace) -> Sequence[Tuple[str, bool]]:
        return []


def AbsolutePath(*args, **kargs):
    return Path(*args, **kargs).absolute()


def yesno(prompt, default: bool=None, add_options=True):
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



