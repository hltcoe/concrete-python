#!/usr/bin/env python
"""
Pretty-prints a Concrete Communication file as JSON
"""

import argparse
import codecs
import sys

from concrete.util import concrete2json


def main():
    # Make stdout output UTF-8, preventing "'ascii' codec can't encode" errors
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)

    parser = argparse.ArgumentParser(description="Pretty Print a Concrete Communication file")
    parser.add_argument('communication_file')
    args = parser.parse_args()

    print concrete2json(args.communication_file)


if __name__ == "__main__":
    main()
