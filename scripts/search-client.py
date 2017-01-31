#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import requests

from concrete.search.ttypes import SearchQuery, SearchType
from concrete.util import set_stdout_encoding
from concrete.util.search_wrapper import SearchClientWrapper
import concrete.version


def print_search_result(result, http_lookup_url):
    for result_item in result.searchResultItems:
        if http_lookup_url:
            print(requests.get(
                http_lookup_url %
                result_item.communicationId
            ).text)
        else:
            print(result_item.communicationId)


def main():
    set_stdout_encoding()

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
    parser.add_argument("--k", type=int, default=10,
                        help="Maximum number of search results to return")
    parser.add_argument("--about", action="store_true",
                        help="Print output of searchService.about()")
    parser.add_argument("--alive", action="store_true",
                        help="Print output of searchService.alive()")
    parser.add_argument("--capabilities", action="store_true",
                        help="Print output of searchService.getCapabilities()")
    parser.add_argument("--corpora", action="store_true",
                        help="Print output of searchService.getCorpora()")
    parser.add_argument("terms", nargs="*")
    concrete.version.add_argparse_argument(parser)
    ns = parser.parse_args()

    with SearchClientWrapper(ns.host, ns.port) as client:
        interactive_mode = True

        if ns.about or ns.alive or ns.capabilities or ns.corpora or ns.terms:
            interactive_mode = False

        if ns.about:
            print("SearchService.about() returned %s" % client.about())
        if ns.alive:
            print("SearchService.alive() returned %s" % client.alive())
        if ns.capabilities:
            print("SearchService.getCapabilities() returned %s" % client.getCapabilities())
        if ns.corpora:
            print("SearchService.getCorpora() returned %s" % client.getCorpora())

        if interactive_mode:
            while True:
                try:
                    line = raw_input('> ').strip().decode('utf-8')
                except EOFError:
                    print()
                    break
                if line:
                    terms = line.split()
                    query = SearchQuery(k=ns.k,
                                        rawQuery=line,
                                        terms=terms,
                                        type=SearchType.COMMUNICATIONS,
                                        userId=ns.user_id)
                    print_search_result(client.search(query), ns.http_lookup_url)
        elif ns.terms:
            query = SearchQuery(k=ns.k,
                                rawQuery=' '.join(ns.terms),
                                terms=ns.terms,
                                type=SearchType.COMMUNICATIONS,
                                userId=ns.user_id)
            print_search_result(client.search(query), None)


if __name__ == '__main__':
    main()
