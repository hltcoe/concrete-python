#!/usr/bin/env python

import argparse

from concrete.util.annotator_wrapper import AnnotatorServiceWrapper
from concrete.util.net import find_port


from time import time

from concrete.services import Annotator
from concrete.metadata.ttypes import AnnotationMetadata


class NoopAnnotator(Annotator.Iface):
    METADATA_TOOL = 'No-op Annotator'

    def annotate(self, communication):
        return communication

    def getMetadata(self,):
        metadata = AnnotationMetadata(tool=self.METADATA_TOOL,
                                      timestamp=int(time()))
        return metadata

    def getDocumentation(self):
        return 'Annotator that returns communication unmodified'

    def shutdown(self):
        pass


def main():
    parser = argparse.ArgumentParser(description='Annotation service for '
                                                 'testing')

    parser.add_argument('--host', dest='host', action='store', type=str,
                        default='localhost', help='Host on which to listen')
    parser.add_argument('-p', '--port', dest='port', action='store', type=int,
                        default=None,
                        help='Port on which to listen (default: auto)')
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
