from argparse import Namespace, ArgumentParser
from typing import Sequence, Tuple, Iterable

from compendium.compendium import Compendium


class Segment:
    """
    Class for compendium commands (init, encrypt, etc.).
    I guess this didn't really need to be a class, but this makes it explicit what commands are needed,
    can provide defaults, and allows for easier iteration over all commands
    can provide defaults, and allows for easier iteration over all commands
    """
    ARGS = []

    @classmethod
    def add_arguments(cls, parser: ArgumentParser):
        """Create any needed arguments"""
        pass

    @classmethod
    def check_arguments(cls, args: Namespace):
        """Check whether all arguments are OK"""
        for arg in cls.ARGS:
            if not hasattr(args, arg):
                setattr(args, arg, None)

    def __init__(self, compendium: Compendium):
        self.compendium = compendium

    def interactive_arguments(self, args: Namespace):
        """Ask for argument values on the command line"""
        pass

    def run(self, args: Namespace):
        """Run this initsegment"""
        pass

    def check(self) -> Iterable[Tuple[str, bool]]:
        return []
