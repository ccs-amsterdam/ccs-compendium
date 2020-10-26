
import sys

from argparse import Namespace

from compendium.command.command import CompendiumCommand
from compendium.initsegment import SEGMENTS


class Init(CompendiumCommand):
    """
    Setup a new compendium folder
    """

    @classmethod
    def add_arguments(cls, parser):
        for segment_class in SEGMENTS:
            segment_class.add_arguments(parser)

    @classmethod
    def run(cls, args: Namespace):
        for segment_class in SEGMENTS:
            try:
                segment_class.check_arguments(args)
            except Exception as e:
                print(f"Invalid argument: {e}", file=sys.stderr)
                return
        initial_segment = SEGMENTS[0]()  # initial initsegment is responsible for creating compendium
        initial_segment.interactive_arguments(args)
        compendium = initial_segment.run(args)
        for segment_class in SEGMENTS[1:]:
            segment = segment_class(compendium)
            segment.interactive_arguments(args)
            segment.run(args)
        compendium.save()



