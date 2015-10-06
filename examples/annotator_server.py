#!/usr/bin/env python

import argparse

from concrete.util.annotator_wrapper import AnnotatorServiceWrapper, NoopAnnotator
from concrete.util.net import find_port


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
