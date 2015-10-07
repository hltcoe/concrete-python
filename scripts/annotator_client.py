#!/usr/bin/env python

import argparse
import codecs
import os
import sys

from thrift import TSerialization
from thrift.protocol import TCompactProtocol

import concrete
from concrete.util import CommunicationWriter
from concrete.util import read_communication_from_file
from concrete.util.annotator_wrapper import AnnotatorClientWrapper


def main():
    # Make stdout output UTF-8, preventing "'ascii' codec can't encode" errors
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)

    parser = argparse.ArgumentParser(description="Interface with a Concrete Annotator service")
    parser.add_argument('--port', required=True, type=int, help="Port to use.")
    parser.add_argument('--host', required=True, default='localhost', help="Hostname to use.")
    parser.add_argument('--input', default='-', help="Input source to use. '-' for stdin; otherwise takes a path to a file. [Default: stdin]")
    parser.add_argument('--output', default='-', help="Output source to use. '-' for stdout; otherwise takes a path to a file. [Default: stdout]")
    args = parser.parse_args()

    if args.input == '-':
        # ???
        handle = os.fdopen(sys.stdin.fileno(), 'rb')
        try:
            bytez = handle.read()
            comm = concrete.Communication()
            TSerialization.deserialize(comm, bytez, protocol_factory=TCompactProtocol.TCompactProtocolFactory())
        finally:
            handle.close()
    else:
        comm = read_communication_from_file(args.input)

    with AnnotatorClientWrapper(args.host, args.port) as client:
        new_comm = client.annotate(comm)

    if args.output == '-':
        new_bytes = TSerialization.serialize(new_comm, protocol_factory=TCompactProtocol.TCompactProtocolFactory())
        handle = os.fdopen(sys.stdout.fileno(), 'wb')
        try:
            handle.write(new_bytes)
        finally:
            handle.close()

    else:
        wrtr = CommunicationWriter(args.output)
        wrtr.write(new_comm)
        wrtr.close()

if __name__ == "__main__":
    main()
