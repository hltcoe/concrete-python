#!/usr/bin/env python

'Pretty-prints a Concrete file as JSON'
from __future__ import print_function
from __future__ import unicode_literals

import concrete.version
import argparse
import codecs

from thrift import TSerialization
from thrift.protocol import TJSONProtocol

from concrete.util import (
    communication_file_to_json,
    tokenlattice_file_to_json,
    read_communication_from_file)
from concrete.util import set_stdout_encoding


def main():
    set_stdout_encoding()

    parser = argparse.ArgumentParser(
        description="Pretty Print a Concrete file")
    parser.add_argument('--concrete_type', default='communication',
                        choices=['communication', 'tokenlattice'],
                        help='Default: communication')
    parser.add_argument('--protocol', default='simple',
                        choices=['simple', 'TJSONProtocol'],
                        help='Default: simple')
    parser.add_argument('--remove-timestamps', action='store_true',
                        help="Removes timestamps from JSON output")
    parser.add_argument('--remove-uuids', action='store_true',
                        help="Removes UUIDs from JSON output")
    parser.add_argument('concrete_file',
                        help='path to input concrete communication file')
    parser.add_argument('json_file', nargs='?', default='-',
                        help='path to output json file')
    concrete.version.add_argparse_argument(parser)
    args = parser.parse_args()

    if args.protocol == 'simple':
        if args.concrete_type == 'communication':
            json_communication = communication_file_to_json(
                args.concrete_file,
                remove_timestamps=args.remove_timestamps,
                remove_uuids=args.remove_uuids
            )
        else:
            json_communication = tokenlattice_file_to_json(
                args.concrete_file
            )
    else:
        if args.concrete_type == 'communication':
            comm = read_communication_from_file(args.concrete_file)
            json_communication = TSerialization.serialize(
                comm, TJSONProtocol.TJSONProtocolFactory()).decode('utf-8')
        else:
            raise NotImplementedError

    if args.json_file == '-':
        print(json_communication)
    else:
        with codecs.open(args.json_file, 'w', encoding='utf-8') as f:
            f.write(json_communication)


if __name__ == "__main__":
    main()
