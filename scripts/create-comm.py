#!/usr/bin/env python2.7

'Convert text file to Concrete Communication file.'

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import codecs

import concrete.version
from concrete.util.file_io import write_communication_to_file
from concrete.util.simple_comm import (
    create_comm, AL_NONE, add_annotation_level_argparse_argument
)


def main():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Convert text file to communication',
    )
    parser.set_defaults(annotation_level=AL_NONE)
    parser.add_argument('text_path', type=str,
                        help='Input text file path (- for stdin)')
    parser.add_argument('concrete_path', type=str,
                        help='Output concrete file path (- for stdout)')
    add_annotation_level_argparse_argument(parser)
    concrete.version.add_argparse_argument(parser)
    ns = parser.parse_args()

    # Won't work on Windows... but that use case is very unlikely
    text_path = '/dev/fd/0' if ns.text_path == '-' else ns.text_path
    concrete_path = (
        '/dev/fd/1' if ns.concrete_path == '-' else ns.concrete_path
    )
    annotation_level = ns.annotation_level

    with codecs.open(text_path, encoding='utf-8') as f:
        comm = create_comm(text_path, f.read(),
                           annotation_level=annotation_level)
        write_communication_to_file(comm, concrete_path)


if __name__ == "__main__":
    main()
