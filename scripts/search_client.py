#!/usr/bin/env python

import concrete.version
import sys
import codecs
import requests
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from concrete.util.search_wrapper import SearchClientWrapper
from concrete.search.ttypes import SearchQuery, SearchType


def main():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Interface with a Concrete Search service'
    )
    parser.add_argument('host',
                        help='Hostname of search service to which to'
                             ' connect.')
    parser.add_argument('port', type=int,
                        help='Port of search service to which to connect.')
    parser.add_argument('--http-lookup-url', type=str,
                        help='Look up result communication text from HTTP '
                             'service via provided URL template, for '
                             'example, http://localhost:3000/comm/id/%%s')
    parser.add_argument('--user-id', type=str,
                        help='user id to send to search service')
    concrete.version.add_argparse_argument(parser)
    ns = parser.parse_args()

    out_f = codecs.getwriter('utf-8')(sys.stdout)

    with SearchClientWrapper(ns.host, ns.port) as client:
        while True:
            try:
                line = raw_input('> ').strip().decode('utf-8')
            except EOFError:
                print
                break
            if line:
                terms = line.split()
                query = SearchQuery(terms=terms,
                                    type=SearchType.COMMUNICATIONS,
                                    userId=ns.user_id)
                results = client.search(query)
                for result in results.searchResults:
                    if ns.http_lookup_url:
                        out_f.write(requests.get(
                            ns.http_lookup_url %
                            result.communicationId
                        ).text + u'\n')
                    else:
                        out_f.write(result.communicationId + u'\n')


if __name__ == '__main__':
    main()
