#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import logging
import sys

from concrete.search.ttypes import SearchQuery, SearchType
from concrete.util import set_stdout_encoding
from concrete.util.search_wrapper import SearchClientWrapper
import concrete.version

try:
    raw_input
except NameError:
    raw_input = input


def execute_search_query(search_client, terms, k):
    logging.debug("executing query '{}'".format(u' '.join(terms)))
    query = SearchQuery(type=SearchType.COMMUNICATIONS, terms=terms, k=k)
    result = search_client.search(query)
    return [
        (item.communicationId, item.score)
        for item in result.searchResultItems
    ]


def unicode_arg(s):
    """Convert argparse argument to Unicode string

    On Python 3, no conversion is necessary
    On Python 2, we convert bytestring to unicode using file system encoding

    See:
      https://codereview.stackexchange.com/questions/124434/get-argument-as-unicode-string-from-argparse-in-python-2-and-3
    """
    if sys.version_info >= (3, 0):
        return s
    else:
        return s.decode(sys.getfilesystemencoding())


def main():
    set_stdout_encoding()

    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Concrete Search client (allows specifying query on '
                    'command line, interactively on the terminal, or '
                    'in batch from standard input).'
    )
    parser.add_argument('--host', default='localhost',
                        help='Hostname of Search service')
    parser.add_argument('--port', type=int, default=9090,
                        help='Port of Search service')
    parser.add_argument('--user-id', type=str,
                        help='user id to send to search service')
    parser.add_argument('-k', '--k', type=int, default=10,
                        help='Maximum number of search results to return per query')
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='Start interactive client (read queries on '
                             'terminal, one at a time, terms delimited by '
                             'spaces).')
    parser.add_argument('-b', '--batch', action='store_true',
                        help='Perform batch of queries (read queries from '
                             'standard input, one per line, terms delimited '
                             'by spaces).')
    parser.add_argument('--with-scores', action='store_true',
                        help='Print score next to each hit (separated by a '
                             'tab).')
    parser.add_argument('--about', action='store_true',
                        help='Print output of searchService.about()')
    parser.add_argument('--alive', action='store_true',
                        help='Print output of searchService.alive()')
    parser.add_argument('--capabilities', action='store_true',
                        help='Print output of searchService.getCapabilities()')
    parser.add_argument('--corpora', action='store_true',
                        help='Print output of searchService.getCorpora()')
    parser.add_argument('-l', '--loglevel', '--log-level',
                        help='Logging verbosity level threshold (to stderr)',
                        default='info')
    parser.add_argument('terms', metavar='term', nargs='*', type=unicode_arg,
                        help='Single query to perform (mutually exclusive with -b -and -i)')
    concrete.version.add_argparse_argument(parser)
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)-15s %(levelname)s: %(message)s',
                        level=args.loglevel.upper())

    with SearchClientWrapper(args.host, args.port) as search_client:

        if args.about:
            print("SearchService.about() returned %s" % search_client.about())
        if args.alive:
            print("SearchService.alive() returned %s" % search_client.alive())
        if args.capabilities:
            print("SearchService.getCapabilities() returned %s" % search_client.getCapabilities())
        if args.corpora:
            print("SearchService.getCorpora() returned %s" % search_client.getCorpora())

        if args.interactive:
            if args.batch:
                raise Exception(
                    'batch mode (-b) cannot be specified for '
                    'interactive client (-i)')
            if args.terms:
                raise Exception(
                    'query terms cannot be specified on command line for '
                    'interactive client (-i)')
            logging.info('starting interactive search client...')
            logging.info('note: query terms are delimited by tabs')
            logging.info('enter a blank query to exit')
            line = raw_input('> ')
            while line:
                terms = unicode_arg(line).split('\t')
                for (comm_id, score) in execute_search_query(search_client, terms, args.k):
                    if args.with_scores:
                        print('{}	{}'.format(comm_id, score))
                    else:
                        print(comm_id)
                line = raw_input('> ')
        elif args.batch:
            logging.info('starting batch non-interactive search client...')
            if args.terms:
                raise Exception(
                    'query terms cannot be specified on command line for '
                    'batch client (-b)')
            logging.info('note: query terms are delimited by tabs')
            for line in sys.stdin:
                terms = line.rstrip('\r\n').split('\t')
                print('\t'.join(
                    (
                        '{} {}'.format(comm_id, score)
                        if args.with_scores else comm_id
                    )
                    for (comm_id, score)
                    in execute_search_query(search_client, terms, args.k)
                ))
        else:
            logging.info('starting single-query non-interactive search client...')
            if args.terms:
                for (comm_id, score) in execute_search_query(search_client, args.terms, args.k):
                    if args.with_scores:
                        print('{}	{}'.format(comm_id, score))
                    else:
                        print(comm_id)
            else:
                logging.warning('No search terms specified')


if __name__ == '__main__':
    main()
