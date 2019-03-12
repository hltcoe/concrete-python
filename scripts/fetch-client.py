#!/usr/bin/env python

"""Command line client for FetchCommunicationService
"""
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import sys
import logging
import time

import concrete.version
from concrete.access.ttypes import FetchRequest
from concrete.util import set_stdout_encoding, is_accelerated
from concrete.util.access_wrapper import (
    FetchCommunicationClientWrapper,
    HTTPFetchCommunicationClientWrapper
)
from concrete.util.file_io import CommunicationWriterTGZ


def main():
    set_stdout_encoding()

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Interface with a Concrete FetchCommunicationService server. "
                    "Supports either THttp/TJSONProtocol (using the '--uri' flag) "
                    "or TSocket/TCompactProtocol (using '--host'/'--port')"
    )
    parser.add_argument("--host", default="localhost",
                        help="Hostname of TSocket/TCompactProtocol FetchCommunicationService")
    parser.add_argument("-p", "--port", type=int, default=9090,
                        help="Port of TSocket/TCompactProtocol FetchCommunicationService")
    parser.add_argument('--uri', '--url',
                        help="URI of THttpServer/TJSONProtocol FetchCommunicationService")
    parser.add_argument("--about", action="store_true",
                        help="Print value of fetch_service.about()")
    parser.add_argument("--alive", action="store_true",
                        help="Print value of fetch_service.alive()")
    parser.add_argument("--count", action="store_true",
                        help="Print value of fetch_service.getCommunicationCount()")
    parser.add_argument("--get-ids", action="store_true",
                        help="Print list of Communication IDs returned by "
                             "fetch_service.getCommunicationIDs(offset, count).  "
                             "The offset and count parameters are set using the "
                             "'--get-ids-offset' and '--get-ids-count' flags")
    parser.add_argument("--get-ids-offset", type=int, default=0, metavar="ID_OFFSET",
                        help="Number of Communication IDs printed using the '--get-ids' flag")
    parser.add_argument("--get-ids-count", type=int, default=20, metavar="ID_COUNT",
                        help="Offset for Communication IDs printed using the '--get-ids' flag")
    parser.add_argument("--save-as-tgz", metavar="TGZ_FILENAME",
                        help="Save fetched Communications to a TGZ archive containing files "
                             "named '[COMMUNICATION_ID].concrete'")
    parser.add_argument('-l', '--loglevel', '--log-level',
                        help='Logging verbosity level threshold (to stderr)',
                        default='info')
    parser.add_argument("comm_id", nargs="*", help="IDs of Communications to be fetched. "
                                                   "If '-' is specified, a list of Communication"
                                                   " IDs will be read from "
                                                   "stdin, one Communication ID per line")
    parser.add_argument("--benchmark", action="store_true",
                        help="Enable Thrift RPC timing instrument.")
    concrete.version.add_argparse_argument(parser)
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)-15s %(levelname)s: %(message)s',
                        level=args.loglevel.upper())

    if args.benchmark:
        if is_accelerated():
            logging.info('Thrift acceleration is enabled.')
        else:
            logging.warning('Thrift acceleration is NOT enabled.')

    if args.uri:
        fetch_wrapper = HTTPFetchCommunicationClientWrapper(args.uri)
    else:
        fetch_wrapper = FetchCommunicationClientWrapper(args.host, args.port)

    with fetch_wrapper as client:
        if args.comm_id:
            fetch_request = FetchRequest()
            if len(args.comm_id) == 1 and args.comm_id[0] == '-':
                fetch_request.communicationIds = [line.strip() for line in sys.stdin.readlines()]
            else:
                fetch_request.communicationIds = args.comm_id

            if args.benchmark:
                start_time = time.time()
            fetch_result = client.fetch(fetch_request)
            if args.benchmark:
                logging.info('Time elapsed in fetch(): {:.4f}s'.format(time.time() - start_time))
            print("Received FetchResult: '%s'" % fetch_result)

        if args.about:
            if args.benchmark:
                start_time = time.time()
            print("FetchCommunicationService.about() returned %s" % client.about())
            if args.benchmark:
                logging.info('Time elapsed in about(): {:.4f}s'.format(time.time() - start_time))
        if args.alive:
            if args.benchmark:
                start_time = time.time()
            print("FetchCommunicationService.alive() returned %s" % client.alive())
            if args.benchmark:
                logging.info('Time elapsed in alive(): {:.4f}s'.format(time.time() - start_time))
        if args.count:
            if args.benchmark:
                start_time = time.time()
            print("FetchCommunicationService.getCommunicationCount() returned %d" %
                  client.getCommunicationCount())
            if args.benchmark:
                logging.info('Time elapsed in getCommunicationCount(): {:.4f}s'.format(
                    time.time() - start_time))
        if args.get_ids:
            print("FetchCommunicationService.getCommunicationIDs(offset=%d, count=%d) returned:" %
                  (args.get_ids_offset, args.get_ids_count))
            if args.benchmark:
                start_time = time.time()
            ids = client.getCommunicationIDs(args.get_ids_offset, args.get_ids_count)
            if args.benchmark:
                logging.info('Time elapsed in getCommunicationIDs(): {:.4f}s'.format(
                    time.time() - start_time))
            for comm_id in ids:
                print("  %s" % comm_id)

        if args.save_as_tgz and args.comm_id:
            if fetch_result.communications:
                with CommunicationWriterTGZ(args.save_as_tgz) as writer:
                    for comm in fetch_result.communications:
                        comm_filename = '%s.concrete' % comm.id
                        print("Saving Communication to TGZ archive '%s' as '%s'" %
                              (args.save_as_tgz, comm_filename))
                        writer.write(comm, comm_filename)


if __name__ == '__main__':
    main()
