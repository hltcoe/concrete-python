#!/usr/bin/env python2.7

'Convert tarball of text files to tarball of Concrete communications.'

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import tarfile
import logging

import concrete.version
from concrete.util.file_io import CommunicationWriterTGZ
from concrete.util.simple_comm import (
    create_comm, AL_NONE, add_annotation_level_argparse_argument
)


def load(path, per_line, annotation_level):
    '''
    Generate communications constructed from text files in specified
    tarball, assigning ids that are meaningful tar-friendly filenames.

    If per_line is True:
    One communication is created for each newline in a file.  Note blank
    lines will produce communications.  The trailing newline is included
    in the communication text.  If a file does not have a terminating
    newline, a communication is nonetheless produced for the last line,
    and a newline is appended to the end of the text.
    '''
    with tarfile.open(path, 'r|*') as tf:
        ti = tf.next()
        while ti is not None:
            if ti.isfile():
                f = tf.extractfile(ti)
                text = f.read().decode('utf-8')

                if per_line:
                    if text.endswith('\n'):
                        text = text[:-1]
                    for (i, line) in enumerate(text.split('\n')):
                        yield create_comm(u'%s/%d' % (ti.name, i),
                                          line + u'\n',
                                          annotation_level=annotation_level)
                else:
                    yield create_comm(ti.name, text,
                                      annotation_level=annotation_level)

            tf.members = []
            ti = tf.next()


def main():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Convert tarball of text files to'
                    ' tarball of concrete communications',
    )
    parser.set_defaults(annotation_level=AL_NONE,
                        log_level='INFO', log_interval=1000)
    parser.add_argument('text_tarball_path', type=str,
                        help='Input text tar file path (- for stdin)')
    parser.add_argument('concrete_tarball_path', type=str,
                        help='Output concrete tar file path (- for stdout)')
    parser.add_argument('--per-line', action='store_true',
                        help='Text files have one document per line (default:'
                             ' each text file is a document)')
    parser.add_argument('--log-interval', type=int,
                        help='Log an info message every log-interval docs')
    parser.add_argument('--log-level', type=str,
                        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR'),
                        help='Logging verbosity level (to stderr)')
    add_annotation_level_argparse_argument(parser)
    concrete.version.add_argparse_argument(parser)
    ns = parser.parse_args()

    # Won't work on Windows... but that use case is very unlikely
    text_tarball_path = (
        '/dev/fd/0'
        if ns.text_tarball_path == '-'
        else ns.text_tarball_path
    )
    concrete_tarball_path = (
        '/dev/fd/1'
        if ns.concrete_tarball_path == '-'
        else ns.concrete_tarball_path
    )
    per_line = ns.per_line
    annotation_level = ns.annotation_level

    logging.basicConfig(
        level=ns.log_level,
        format='%(asctime)-15s %(levelname)s: %(message)s'
    )

    with CommunicationWriterTGZ(concrete_tarball_path) as writer:
        for (i, comm) in enumerate(load(text_tarball_path, per_line,
                                        annotation_level)):
            if (i + 1) % ns.log_interval == 0:
                logging.info(u'writing doc %d (%s)...' % (i + 1, comm.id))
            writer.write(comm, comm.id)


if __name__ == "__main__":
    main()
