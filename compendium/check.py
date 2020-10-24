"""
Generic checks for compendium completeness and consistence
"""

import logging

from argparse import Namespace, ArgumentParser

from compendium.segment import AbsolutePath, Segment
from compendium.init import get_segments

_CHECK_OK = '\u2714\u2009'
_CHECK_FAIL = '\u2718\u2009'


def add_subparser(subparsers):
    parser = subparsers.add_parser('check', help=__doc__)
    parser.add_argument("folder", nargs="?", default=".", type=AbsolutePath,
                        help="Compendium folder (default: current folder)")


def run(args: Namespace):
    if not args.folder:
        raise ValueError("Cannot check without folder specified")
    print(f"\nRunning checks on compendium {args.folder}:")
    for segment in get_segments():
        for check, outcome in segment.check(args):
            print(f"[{_CHECK_OK if outcome else _CHECK_FAIL}] {check}")


_run_check = run


class CheckSegment(Segment):
    """Init segment to run the check"""
    ARGS = ["skipcheck"]

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("--skipcheck", action="store_true",
                            help="Skip the check after init")

    def run(self, args: Namespace):
        if not args.skipcheck:
            _run_check(args)

def get_cycles(graph):
    def cycles_node(graph, node, visited=None):
        # Can I find a cycle in the depth-first graph starting from this node?
        if visited is None:
            visited = set()
        for neighbour in graph.get(node, []):
            #print(f"{node} -> {neighbour} (visited: {visited})")
            if neighbour in visited:
                yield neighbour
            else:
                visited.add(neighbour)
                yield from cycles_node(graph, neighbour, visited)

    # for any node, can you find a cycle?
    for n in graph:
        yield from cycles_node(graph, n)


def do_check(args):
    """
    Run sanity checks on the package
    """
    logging.info("Checking consistency of dependency graph")
    inputs, outputs, graph = set(), set(), defaultdict(set)
    for action in get_actions():
        inputs |= set(action.inputs)
        outputs |= set(action.targets)
        for output in action.targets:
            for input in action.inputs:
                graph[input].add(output)
    errors = []
    # check: all inputs need to be either in raw and exist, in private_raw, or in outputs
    for input in inputs - outputs:
        if contained_in(DATA_RAW, input):
            errors.append(f"Input file {input} does not exist")
        elif not contained_in(DATA_PRIVATE, input):
            errors.append(f"Intermediate file {input} is not produced by any script")
    # check that graph does not contain any cycles
    cycles = set(get_cycles(graph))
    for cycle in cycles:
        errors.append(f"Cyclical dependency for file {cycle}")
    if errors:
        print("Package checking resulted in one or more errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        sys.exit(1)