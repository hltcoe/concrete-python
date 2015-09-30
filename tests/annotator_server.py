#!/usr/bin/env python

import argparse
import time

import concrete
from concrete.services import Annotator
from concrete.util import annotator_wrapper


class FakeAnnotator(Annotator.Iface):
    def annotate(self, communication):
        return communication

    def getMetadata(self,):
        metadata = concrete.AnnotationMetadata(tool='Fake Annotator',
                                               timestamp=int(time.time()))
        return metadata

    def getDocumentation(self):
        return 'Annotator that returns communication'

    def shutdown(self):
        pass


def main():
    parser = argparse.ArgumentParser(description='Annotation service for '
                                                 'testing')

    parser.add_argument('--host', dest='host', action='store', type=str,
                        default='localhost', help='Host on which to listen')
    parser.add_argument('-p', '--port', dest='port', action='store', type=str,
                        default=33222, help='Port on which to listen')
    args = parser.parse_args()

    handler = FakeAnnotator()

    server = annotator_wrapper.AnnotatorServiceWrapper(handler)
    server.serve(args.host, args.port)


if __name__ == '__main__':
    main()
