#!/usr/bin/env python

from __future__ import unicode_literals
import concrete.version
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from concrete.util import CommunicationReader, CommunicationWriter, FileType
from concrete.util.annotate_wrapper import AnnotateCommunicationClientWrapper
from concrete.util import set_stdout_encoding


def main():
    set_stdout_encoding()

    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="Interface with a Concrete AnnotateCommunicationService"
    )
    parser.add_argument('host',
                        help="Hostname of annotate service to which to"
                             " connect.")
    parser.add_argument('port', type=int,
                        help="Port of annotate service to which to connect.")
    parser.add_argument('--input', default='-',
                        help="Input source to use. '-' for stdin; otherwise"
                             " takes a path to a file.")
    parser.add_argument('--output', default='-',
                        help="Output source to use. '-' for stdout; otherwise"
                             " takes a path to a file.")
    concrete.version.add_argparse_argument(parser)
    args = parser.parse_args()

    # Won't work on Windows
    if args.input == '-':
        reader_kwargs = dict(filetype=FileType.STREAM)
        input_path = '/dev/fd/0'
    else:
        reader_kwargs = dict()
        input_path = args.input
    output_path = '/dev/fd/1' if args.output == '-' else args.output

    reader = CommunicationReader(input_path, **reader_kwargs)
    with AnnotateCommunicationClientWrapper(args.host, args.port) as client:
        with CommunicationWriter(output_path) as writer:
            for (comm, _) in reader:
                writer.write(client.annotate(comm))


if __name__ == "__main__":
    main()
