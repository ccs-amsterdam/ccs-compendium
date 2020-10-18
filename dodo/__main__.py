"""
Dodo Open Science Compendium - Commands to help create and maintain the compendium

Use `dodo init --help` for information on how to create a new compendium
Use `dodo --help` for a list of all available commands
"""
import argparse
import logging
import sys

from dodo import init, encrypt


def main():
    parser = argparse.ArgumentParser(description=__doc__, prog='dodo')
    parser.add_argument("--verbose", "-v", help="Verbose output", action="store_true")
    parser.add_argument("--quiet", "-q", help="Quiet (minimal output)", action="store_true")
    subparsers = parser.add_subparsers(help='Sub commands', dest='command')
    subparsers.required = True
    init.add_subparser(subparsers)
    encrypt.add_subparser(subparsers)

    if len(sys.argv) == 1:
        print(__doc__, file=sys.stderr)
    args = parser.parse_args()

    level = (logging.DEBUG if args.verbose else (logging.WARN if args.quiet else logging.INFO))
    logging.basicConfig(level=level, format='[%(levelname)-5s] %(message)s')

    globals()[args.command].run(args)


if __name__ == '__main__':
    main()