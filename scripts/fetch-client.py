#!/usr/bin/env python

"""Command line client for FetchCommunicationService
"""

import argparse

import concrete.version
from concrete.access import FetchCommunicationService
from concrete.access.ttypes import FetchRequest
from concrete.util.file_io import write_communication_to_file
from concrete.util.thrift_factory import factory


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Command line client for interacting with a FetchCommunicationService server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-p", "--port", type=int, default=9090,
                        help="Port of FetchCommunicationService server")
    parser.add_argument("-s", "--server", default="localhost",
                        help="Hostname of FetchCommunicationService server")
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
    parser.add_argument("--get-ids-offset", type=int, default=0,
                        help="Number of Communication IDs printed using the '--get-ids' flag")
    parser.add_argument("--get-ids-count", type=int, default=20,
                        help="Offset for Communication IDs printed using the '--get-ids' flag")
    parser.add_argument("--save", action="store_true",
                        help="Save fetched Communications to disk as "
                        "'[COMMUNICATION_ID].concrete'")
    parser.add_argument("comm_id", nargs="*", help="IDs of Communications to be fetched")
    concrete.version.add_argparse_argument(parser)
    args = parser.parse_args()

    socket = factory.createSocket(args.server, args.port)
    transport = factory.createTransport(socket)
    protocol = factory.createProtocol(transport)
    client = FetchCommunicationService.Client(protocol)
    transport.open()

    if args.comm_id:
        fetch_request = FetchRequest()
        fetch_request.communicationIds = args.comm_id
        fetch_result = client.fetch(fetch_request)
        print "Received FetchResult: '%s'" % fetch_result

    if args.about:
        print "FetchCommunicationService.about() returned %s" % client.about()
    if args.alive:
        print "FetchCommunicationService.alive() returned %s" % client.alive()
    if args.count:
        print "FetchCommunicationService.getCommunicationCount() returned %d" % \
            client.getCommunicationCount()
    if args.get_ids:
        print "FetchCommunicationService.getCommunicationIDs(offset=%d, count=%d) returned:" % \
            (args.get_ids_offset, args.get_ids_count)
        for comm_id in client.getCommunicationIDs(args.get_ids_offset, args.get_ids_count):
            print "  %s" % comm_id

    if args.save:
        if fetch_result.communications:
            for comm in fetch_result.communications:
                comm_filename = '%s.concrete' % comm.id
                print "Saving Communication as '%s'" % comm_filename
                write_communication_to_file(comm, comm_filename)
