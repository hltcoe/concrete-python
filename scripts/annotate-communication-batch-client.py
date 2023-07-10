#!/usr/bin/env python

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import logging
import sys

from thrift.protocol.TProtocol import TProtocolException

import concrete.version
from concrete import ServicesException
from concrete.util import (
    CommunicationReader, CommunicationWriterZip, FileType,
    AnnotateCommunicationBatchClientWrapper, HTTPAnnotateCommunicationBatchClientWrapper,
)


def main():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="Interface with a Concrete AnnotateCommunicationBatchService server. "
        "Supports either THttp/TJSONProtocol (using the '--uri' flag) "
        "or TSocket/TCompactProtocol (using '--host'/'--port')"
    )
    parser.add_argument('--host', default='localhost',
                        help="Hostname of TSocket/TCompactProtocol "
                             "AnnotateCommunicationBatchService")
    parser.add_argument('-p', '--port', type=int, default=9090,
                        help="Port of TSocket/TCompactProtocol AnnotateCommunicationBatchService")
    parser.add_argument('--uri', '--url',
                        help="URI of THttpServer/TJSONProtocol AnnotateCommunicationBatchService")
    parser.add_argument('-l', '--loglevel', '--log-level',
                        help='Logging verbosity level threshold (to stderr)',
                        default='info')
    parser.add_argument('--input', default='-',
                        help="Input source to use. '-' for stdin; otherwise"
                             " takes a path to a file.")
    parser.add_argument('--output', default='-',
                        help="Output source to use. '-' for stdout; otherwise"
                             " takes a path to a file.  Output format will be a ZIP archive.")
    parser.add_argument('--recursive', action='store_true',
                        help="If set, read files from input recursively, allowing input to be a "
                             "directory containing Communication files (potentially nested in "
                             "subdirectories).")
    parser.add_argument('--followlinks', action='store_true',
                        help="If set, follow symlinks when recursing input directories.")
    concrete.version.add_argparse_argument(parser)
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)-15s %(levelname)s: %(message)s',
                        level=args.loglevel.upper())

    # Won't work on Windows
    if args.input == '-':
        reader_kwargs = dict(filetype=FileType.STREAM)
        input_path = '/dev/fd/0'
    else:
        reader_kwargs = dict(recursive=args.recursive, followlinks=args.followlinks)
        input_path = args.input
    output_path = '/dev/fd/1' if args.output == '-' else args.output

    def _run(client):
        reader = CommunicationReader(input_path, **reader_kwargs)
        try:
            annotated_comms = client.annotate([comm for (comm, _) in reader])
        except ServicesException as ex:
            logging.error(f'Service raised exception: {ex.message}')
            logging.info('Check server log for more information')
            sys.exit(1)

        with CommunicationWriterZip(output_path) as writer:
            for annotated_comm in annotated_comms:
                writer.write(annotated_comm)

    if args.uri:
        try:
            with HTTPAnnotateCommunicationBatchClientWrapper(args.uri) as client:
                _run(client)
        except TProtocolException:
            logging.exception(
                "Successfully connected to the URI '{}' using HTTP, but the URI does not "
                "appear to be an AnnotateCommunicationService endpoint that uses the "
                "Thrift THttp transport and TJSONProtocol encoding".format(args.uri))
    else:
        with AnnotateCommunicationBatchClientWrapper(args.host, args.port) as client:
            _run(client)


if __name__ == "__main__":
    main()
