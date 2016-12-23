#!/usr/bin/env python

'Pretty-prints a Concrete file as JSON'

import concrete.version
import argparse
import codecs
import sys

from thrift import TSerialization
from thrift.protocol import TJSONProtocol

from concrete.util import (
    communication_file_to_json,
    tokenlattice_file_to_json,
    read_communication_from_file)


def main():
    # Make stdout output UTF-8, preventing "'ascii' codec can't encode" errors
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)

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
    parser.add_argument('concrete_file')
    parser.add_argument('json_file', nargs='?', default='STDOUT')
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
            json_communication = tokenlattice_file_to_json(args.concrete_file)
    else:
        if args.concrete_type == 'communication':
            comm = read_communication_from_file(args.concrete_file)
            json_communication = TSerialization.serialize(
                comm, TJSONProtocol.TJSONProtocolFactory())
        else:
            raise NotImplementedError

    if args.json_file == 'STDOUT':
        print json_communication
    else:
        f = codecs.open(args.json_file, "w", encoding="utf-8")
        f.write(json_communication)
        f.close()


if __name__ == "__main__":
    main()
