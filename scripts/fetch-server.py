#!/usr/bin/env python

"""Command line FetchCommunicationService server

fetch-server.py is intended to make it as easy as possible to stand up
a FetchCommunicationService that serves Communication files stored on
the local filesystem.  When you run the command:

  fetch-server.py communications_source

this script should "just work", doing what a naive user would
reasonably expect should happen, regardless of whether
communications_source is:

- a directory of files (possibly with sub-directories, and possibly
   with files that aren't Communications)
- a TGZ file of Communications
- a ZIP file of Communications

"""
from __future__ import unicode_literals

import argparse
import logging
import os
import os.path
import zipfile

import humanfriendly

import concrete.version
from concrete.util.access import CommunicationContainerFetchHandler
from concrete.util.access_wrapper import FetchCommunicationServiceWrapper
from concrete.util.comm_container import (
    DirectoryBackedCommunicationContainer,
    MemoryBackedCommunicationContainer,
    ZipFileBackedCommunicationContainer)
from concrete.util import set_stdout_encoding


def main():
    set_stdout_encoding()

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    parser = argparse.ArgumentParser(
        description="Command line FetchCommunicatonService server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("communications_source",
                        help="A path to {1} a (possibly nested) directory of "
                        "Communications named using the convention "
                        "'[COMMUNICATION_ID].[comm|concrete|gz], "
                        "{2} a ZIP file of Communications, or "
                        "{3} a file (which can be a .tgz or .tar file) containing "
                        "one or more Communications, all of which will be read "
                        "into memory on startup")
    parser.add_argument("--host", default=None,
                        help="Network interface for server to listen on "
                        "(e.g. 'localhost', '0.0.0.0')")
    parser.add_argument("-p", "--port", type=int, default=9090,
                        help="Port for server to listen on")
    parser.add_argument("--max-file-size", type=str, default="1GiB",
                        help="Maximum size of (non-ZIP) files that can be read into memory "
                        "(e.g. '2G', '300MB')")
    concrete.version.add_argparse_argument(parser)
    args = parser.parse_args()

    if os.path.isdir(args.communications_source):
        comm_container = DirectoryBackedCommunicationContainer(args.communications_source)
    elif zipfile.is_zipfile(args.communications_source):
        comm_container = ZipFileBackedCommunicationContainer(args.communications_source)
    else:
        max_file_size = humanfriendly.parse_size(args.max_file_size, binary=True)
        comm_container = MemoryBackedCommunicationContainer(args.communications_source,
                                                            max_file_size=max_file_size)
    logging.info('Using Communication Container of type %s' % type(comm_container))
    handler = CommunicationContainerFetchHandler(comm_container)

    fetch_service = FetchCommunicationServiceWrapper(handler)
    logging.info("Waiting for connections on port %d..." % args.port)
    fetch_service.serve(args.host, args.port)


if __name__ == '__main__':
    main()
