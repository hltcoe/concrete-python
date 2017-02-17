#!/usr/bin/env python

"""Simple webserver with Fetch/Store RPC support

A simple Bottle webserver useful for testing **concrete-js** programs
that interact with Fetch and Store servers.

Implements an HTTP server that serves static files (e.g. HTML, JS and
CSS) and provides::

- a filesystem-backed :mod:`.FetchCommunicationService`
  at URL `/fetch_http_endpoint/`

- a directory-backed :mod:`.StoreCommunicationService`
  at URL `/store_http_endpoint/`

"""

from __future__ import print_function
import argparse
import logging
import os.path
import zipfile

import bottle
import humanfriendly
from thrift.protocol import TJSONProtocol
from thrift.server import TServer
from thrift.transport import TTransport

from concrete.access import FetchCommunicationService, StoreCommunicationService
from concrete.util.access import (
    CommunicationContainerFetchHandler,
    DirectoryBackedStoreHandler)
from concrete.util.comm_container import (
    DirectoryBackedCommunicationContainer,
    MemoryBackedCommunicationContainer,
    ZipFileBackedCommunicationContainer)


class AccessHTTPServer(object):
    # DANGER WILL ROBINSON!  We are using class variables
    # to store values accessed by the Bottle route functions
    # below.
    FETCH_HANDLER = None
    FETCH_TSERVER = None
    STORE_HANDLER = None
    STORE_TSERVER = None
    STATIC_PATH = None

    def __init__(self, host, port, static_path, fetch_handler, store_handler):
        self.host = host
        self.port = port

        AccessHTTPServer.STATIC_PATH = static_path

        AccessHTTPServer.FETCH_HANDLER = fetch_handler
        fetch_processor = FetchCommunicationService.Processor(fetch_handler)
        fetch_pfactory = TJSONProtocol.TJSONProtocolFactory()
        AccessHTTPServer.FETCH_TSERVER = TServer.TServer(
            fetch_processor, None, None, None, fetch_pfactory, fetch_pfactory)

        AccessHTTPServer.STORE_HANDLER = store_handler
        store_processor = StoreCommunicationService.Processor(store_handler)
        store_pfactory = TJSONProtocol.TJSONProtocolFactory()
        AccessHTTPServer.STORE_TSERVER = TServer.TServer(
            store_processor, None, None, None, store_pfactory, store_pfactory)

    def serve(self):
        bottle.run(host=self.host, port=self.port)


@bottle.post('/fetch_http_endpoint/')
def fetch_http_endpoint():
    return thrift_endpoint(AccessHTTPServer.FETCH_TSERVER)


@bottle.post('/store_http_endpoint/')
def store_http_endpoint():
    return thrift_endpoint(AccessHTTPServer.STORE_TSERVER)


@bottle.route('/<filepath:path>')
def server_static(filepath):
    return bottle.static_file(filepath, root=AccessHTTPServer.STATIC_PATH)


def thrift_endpoint(tserver):
    """Thrift RPC endpoint
    """
    itrans = TTransport.TFileObjectTransport(bottle.request.body)
    itrans = TTransport.TBufferedTransport(
        itrans, int(bottle.request.headers['Content-Length']))
    otrans = TTransport.TMemoryBuffer()

    iprot = tserver.inputProtocolFactory.getProtocol(itrans)
    oprot = tserver.outputProtocolFactory.getProtocol(otrans)

    tserver.processor.process(iprot, oprot)
    bytestring = otrans.getvalue()

    headers = dict()
    headers['Content-Length'] = len(bytestring)
    headers['Content-Type'] = "application/x-thrift"
    return bottle.HTTPResponse(bytestring, **headers)


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=''
    )
    parser.add_argument('fetch_source')
    parser.add_argument('--host', default='localhost',
                        help='Host interface to listen on')
    parser.add_argument('-p', '--port', type=int, default=8080)
    parser.add_argument('-l', '--loglevel', choices=('DEBUG', 'INFO', 'WARNING', 'ERROR'),
                        help='Logging verbosity level threshold (to stderr)')
    parser.add_argument('--static-path', default='.',
                        help='Path where HTML files are stored')
    parser.add_argument('--store-path', default='.',
                        help='Path where Communications should be stored')
    parser.add_argument('--max-file-size', type=str, default='1GiB',
                        help="Maximum size of (non-ZIP) files that can be read into memory "
                        "(e.g. '2G', '300MB')")
    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)7s:  %(message)s', level=args.loglevel)

    comm_container = {}
    if os.path.isdir(args.fetch_source):
        comm_container = DirectoryBackedCommunicationContainer(args.fetch_source)
    elif zipfile.is_zipfile(args.fetch_source):
        comm_container = ZipFileBackedCommunicationContainer(args.fetch_source)
    else:
        max_file_size = humanfriendly.parse_size(args.max_file_size, binary=True)
        comm_container = MemoryBackedCommunicationContainer(args.fetch_source,
                                                            max_file_size=max_file_size)

    fetch_handler = CommunicationContainerFetchHandler(comm_container)
    store_handler = DirectoryBackedStoreHandler(args.store_path)

    ahs = AccessHTTPServer(args.host, args.port, args.static_path, fetch_handler, store_handler)
    ahs.serve()


if __name__ == '__main__':
    main()
