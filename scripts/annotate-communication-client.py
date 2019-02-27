#!/usr/bin/env python

from __future__ import unicode_literals
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import logging

from thrift.protocol.TProtocol import TProtocolException
from thrift.transport.TTransport import TTransportException

import concrete.version
from concrete.util import CommunicationReader, CommunicationWriter, FileType
from concrete.util.annotate_wrapper import (
    AnnotateCommunicationClientWrapper,
    HTTPAnnotateCommunicationClientWrapper
)
from concrete.util import set_stdout_encoding


def main():
    set_stdout_encoding()

    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="Interface with a Concrete AnnotateCommunicationService server. "
        "Supports either THttp/TJSONProtocol (using the '--uri' flag) "
        "or TSocket/TCompactProtocol (using '--host'/'--port')"
    )
    parser.add_argument('--host', default='localhost',
                        help="Hostname of TSocket/TCompactProtocol AnnotateCommunicationService")
    parser.add_argument('-p', '--port', type=int, default=9090,
                        help="Port of TSocket/TCompactProtocol AnnotateCommunicationService")
    parser.add_argument('--uri', '--url',
                        help="URI of THttpServer/TJSONProtocol AnnotateCommunicationService")
    parser.add_argument('-l', '--loglevel', '--log-level',
                        help='Logging verbosity level threshold (to stderr)',
                        default='info')
    parser.add_argument('--input', default='-',
                        help="Input source to use. '-' for stdin; otherwise"
                             " takes a path to a file.")
    parser.add_argument('--output', default='-',
                        help="Output source to use. '-' for stdout; otherwise"
                             " takes a path to a file.")
    concrete.version.add_argparse_argument(parser)
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)-15s %(levelname)s: %(message)s',
                        level=args.loglevel.upper())

    # Won't work on Windows
    if args.input == '-':
        reader_kwargs = dict(filetype=FileType.STREAM)
        input_path = '/dev/fd/0'
    else:
        reader_kwargs = dict()
        input_path = args.input
    output_path = '/dev/fd/1' if args.output == '-' else args.output

    reader = CommunicationReader(input_path, **reader_kwargs)
    if args.uri:
        try:
            with HTTPAnnotateCommunicationClientWrapper(args.uri) as client:
                with CommunicationWriter(output_path) as writer:
                    for (comm, _) in reader:
                        writer.write(client.annotate(comm))
        except TProtocolException as ex:
            logging.error(ex)
            logging.error(
                "Successfully connected to the URI '{}' using HTTP, but the URI does not "
                "appear to be an AnnotateCommunicationService endpoint that uses the "
                "Thrift THttp transport and TJSONProtocol encoding".format(args.uri))
    else:
        try:
            with AnnotateCommunicationClientWrapper(args.host, args.port) as client:
                with CommunicationWriter(output_path) as writer:
                    for (comm, _) in reader:
                        writer.write(client.annotate(comm))
        except TTransportException:
            pass


if __name__ == "__main__":
    main()
