#!/usr/bin/env python

import concrete.version
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from concrete.util import CommunicationReader, CommunicationWriter
from concrete.util.annotator_wrapper import AnnotatorClientWrapper


def main():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="Interface with a Concrete Annotator service"
    )
    parser.add_argument('host',
                        help="Hostname of annotator service to which to"
                             " connect.")
    parser.add_argument('port', type=int,
                        help="Port of annotator service to which to connect.")
    parser.add_argument('--input', default='-',
                        help="Input source to use. '-' for stdin; otherwise"
                             " takes a path to a file.")
    parser.add_argument('--output', default='-',
                        help="Output source to use. '-' for stdout; otherwise"
                             " takes a path to a file.")
    concrete.version.add_argparse_argument(parser)
    args = parser.parse_args()

    # Won't work on Windows... but that use case is very unlikely
    input_path = '/dev/fd/0' if (args.input) == '-' else args.input
    output_path = '/dev/fd/1' if (args.output) == '-' else args.output

    reader = CommunicationReader(input_path)
    with AnnotatorClientWrapper(args.host, args.port) as client:
        with CommunicationWriter(output_path) as writer:
            for (comm, _) in reader:
                writer.write(client.annotate(comm))


if __name__ == "__main__":
    main()
