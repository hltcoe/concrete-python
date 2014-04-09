#!/usr/bin/env python
"""
Pretty-prints a Concrete Communication file as JSON
"""

import argparse
import codecs
import json
import sys

from concrete import Communication
from thrift import TSerialization
from thrift.protocol import TJSONProtocol



def main():
    # Make stdout output UTF-8, preventing "'ascii' codec can't encode" errors
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)

    parser = argparse.ArgumentParser(description="Pretty Print a Concrete Communication file")
    parser.add_argument('communication_file')
    args = parser.parse_args()

    concrete2json(args.communication_file)


def concrete2json(communication_filename):
    comm = Communication()

    comm_bytestring = open(communication_filename).read()
    TSerialization.deserialize(comm, comm_bytestring)

    comm_json_string = TSerialization.serialize(comm, TJSONProtocol.TSimpleJSONProtocolFactory())
    comm_json = json.loads(comm_json_string)
    print json.dumps(comm_json, indent=2, separators=(',', ': '), ensure_ascii=False, sort_keys=True)


if __name__ == "__main__":
    main()
