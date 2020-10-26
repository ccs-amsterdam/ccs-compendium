

import logging
import sys

from argparse import Namespace
from collections import defaultdict

from compendium.command.command import CompendiumCommand
from compendium.compendium import Compendium
from compendium.initsegment import SEGMENTS
from compendium.util import contained_in

_CHECK_OK = '\u2714\u2009'
_CHECK_FAIL = '\u2718\u2009'


class Check(CompendiumCommand):
    """
    Generic checks for compendium completeness and consistence
    """

    @classmethod
    def run(self, args: Namespace):
        compendium = Compendium(args.folder)
        run_checks(compendium)


def run_checks(compendium: Compendium):
    for segment in SEGMENTS:
        for check, outcome in segment(compendium).check():
            print(f"[{_CHECK_OK if outcome else _CHECK_FAIL}] {check}")


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