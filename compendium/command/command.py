from argparse import Namespace
from pathlib import Path

from compendium.compendium import Compendium


class CompendiumCommand:
    """
    (static) Class for compendium commands (init, encrypt, etc.).
    I guess this didn't really need to be a class, but this makes it explicit what commands are needed,
    can provide defaults, and allows for easier iteration over all commands
    Note that by default, this docstring will be displayed as help text for the command.
    """
    name: str = None

    @classmethod
    def get_name(cls):
        return cls.name if cls.name is not None else cls.__name__.lower()

    @classmethod
    def add_subparser(cls, subparsers):
        parser = subparsers.add_parser(cls.get_name(), help=cls.__doc__)
        cls.add_arguments(parser)

    @classmethod
    def add_arguments(cls, parser):
        """Add any extra arguments"""
        pass

    @classmethod
    def run(cls, args: Namespace):
        compendium = Compendium(args.folder or Path.cwd())
        cls.do_run(compendium, args)
        compendium.save()

    @classmethod
    def do_run(cls, compendium: Compendium, args: Namespace):
        pass