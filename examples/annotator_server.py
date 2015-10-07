#!/usr/bin/env python

import argparse

from concrete.util.annotator_wrapper import AnnotatorServiceWrapper
from concrete.util.net import find_port

# NOTE: must be run from repository root for this import to work
# (this is not an absolute import because tests may be removed from the
#  package index, i.e., installed modules)
from tests.annotators import NoopAnnotator


def main():
    parser = argparse.ArgumentParser(description='Annotation service for '
                                                 'testing')

    parser.add_argument('--host', dest='host', action='store', type=str,
                        default='localhost', help='Host on which to listen')
    parser.add_argument('-p', '--port', dest='port', action='store', type=int,
                        default=None, help='Port on which to listen (default: auto)')
    args = parser.parse_args()

    host = args.host
    if args.port is None:
        port = find_port()
    else:
        port = args.port

    print 'Serving on %s:%d...' % (host, port)

    handler = NoopAnnotator()

    server = AnnotatorServiceWrapper(handler)
    server.serve(host, port)


if __name__ == '__main__':
    main()
