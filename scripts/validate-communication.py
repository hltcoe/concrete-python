#!/usr/bin/env python

"""
Command line script to (partially) validate a Concrete Communication

This script is a thin wrapper around the functionality in the
concrete.validate library.
"""

import argparse
import logging

import concrete.version
from concrete.validate import validate_communication_file


def main():
    parser = argparse.ArgumentParser(
        description="Validate a Concrete Communication file")
    parser.add_argument('communication_file')
    parser.add_argument('-l', '--loglevel', choices=['debug', 'info',
                                                     'warning', 'error'],
                        help="Log level threshold")
    concrete.version.add_argparse_argument(parser)
    args = parser.parse_args()

    # Set logging level
    if args.loglevel:
        lowercase_loglevel = args.loglevel.lower()
        if lowercase_loglevel == 'debug':
            loglevel = logging.DEBUG
        elif lowercase_loglevel == 'info':
            loglevel = logging.INFO
        elif lowercase_loglevel == 'warning':
            loglevel = logging.WARNING
        elif lowercase_loglevel == 'error':
            loglevel = logging.ERROR
        else:
            loglevel = logging.DEBUG
    else:
        loglevel = logging.DEBUG
    logging.basicConfig(format='%(levelname)7s:  %(message)s', level=loglevel)

    validate_communication_file(args.communication_file)


if __name__ == "__main__":
    main()
