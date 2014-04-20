#!/usr/bin/env python
"""
Pretty-prints a Concrete Communication file as JSON
"""

import argparse
import codecs
import sys

from concrete.util import communication_file_to_json


def main():
    # Make stdout output UTF-8, preventing "'ascii' codec can't encode" errors
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)

    parser = argparse.ArgumentParser(description="Pretty Print a Concrete Communication file")
    parser.add_argument('communication_file')
    parser.add_argument('json_file', nargs='?', default='STDOUT')
    args = parser.parse_args()

    if args.json_file == 'STDOUT':
        print communication_file_to_json(args.communication_file)
    else:
        f = codecs.open(args.json_file, "w", encoding="utf-8")
        f.write(communication_file_to_json(args.communication_file))
        f.close()


if __name__ == "__main__":
    main()
