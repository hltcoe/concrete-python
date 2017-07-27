#!/usr/bin/env python

"""
Command line script to (partially) validate a Concrete Communication

This script is a thin wrapper around the functionality in the
concrete.validate library.
"""
from __future__ import unicode_literals

import argparse
import logging

import concrete.version
from concrete.validate import validate_communication_file
from concrete.util import set_stdout_encoding


def main():
    set_stdout_encoding()

    parser = argparse.ArgumentParser(
        description="Validate a Concrete Communication file")
    parser.add_argument('communication_file')
    parser.add_argument('-l', '--loglevel',
                        help='Logging verbosity level threshold (to stderr)',
                        default='info')
    concrete.version.add_argparse_argument(parser)
    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)7s:  %(message)s', level=args.loglevel.upper())

    validate_communication_file(args.communication_file)


if __name__ == "__main__":
    main()
