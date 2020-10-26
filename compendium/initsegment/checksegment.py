from argparse import ArgumentParser, Namespace


from compendium.initsegment.segment import Segment

class CheckSegment(Segment):
    """Init segment to run the checks"""
    ARGS = ["skipcheck"]

    @classmethod
    def add_arguments(cls, parser: ArgumentParser):
        parser.add_argument("--skipcheck", action="store_true",
                            help="Skip the check after init")

    def run(self, args: Namespace):
        if not args.skipcheck:
            import compendium.command.check
            compendium.command.check.run_checks(self.compendium)