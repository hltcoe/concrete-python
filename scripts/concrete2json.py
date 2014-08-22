#!/usr/bin/env python
"""
Pretty-prints a Concrete file as JSON
"""

import argparse
import codecs
import sys

from concrete.util import communication_file_to_json, tokenlattice_file_to_json

type_to_fn = {}
type_to_fn['communication'] = communication_file_to_json
type_to_fn['tokenlattice'] = tokenlattice_file_to_json

def main():
    # Make stdout output UTF-8, preventing "'ascii' codec can't encode" errors
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)

    parser = argparse.ArgumentParser(description="Pretty Print a Concrete file")
    parser.add_argument('--concrete_type', default='communication', choices=type_to_fn.keys(),
                        help='Default: communication')
    parser.add_argument('concrete_file')
    parser.add_argument('json_file', nargs='?', default='STDOUT')
    args = parser.parse_args()

    conc_obj = type_to_fn[args.concrete_type](args.concrete_file)

    if args.json_file == 'STDOUT':
        print conc_obj
    else:
        f = codecs.open(args.json_file, "w", encoding="utf-8")
        f.write(conc_obj)
        f.close()


if __name__ == "__main__":
    main()
