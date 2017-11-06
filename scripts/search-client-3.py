#!/usr/bin/env python3

import logging

from concrete.search.ttypes import SearchQuery, SearchType
from concrete.util import SearchClientWrapper


def execute_search_query(search_client, terms, k):
    logging.debug("executing query '{}'".format(' '.join(terms)))
    query = SearchQuery(type=SearchType.COMMUNICATIONS, terms=terms, k=k)
    result = search_client.search(query)
    return [
        (item.communicationId, item.score)
        for item in result.searchResultItems
    ]


def main():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    import sys

    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Concrete Search client (allows specifying query on '
                    'command line, interactively on the terminal, or '
                    'in batch from standard input).'
    )
    parser.add_argument("--host", default="localhost",
                        help='Hostname of Search service')
    parser.add_argument("--port", type=int, default=9090,
                        help='Port of Search service')
    parser.add_argument("-k", type=int, default=10,
                        help='Maximum number of hits to return per query.')
    parser.add_argument('-i', action='store_true',
                        help='Start interactive client (read queries on '
                             'terminal, one at a time, terms delimited by '
                             'spaces).')
    parser.add_argument('-b', action='store_true',
                        help='Perform batch of queries (read queries from '
                             'standard input, one per line, terms delimited '
                             'by spaces).')
    parser.add_argument('--with-scores', action='store_true',
                        help='Print score next to each hit (separated by a '
                             'tab).')
    parser.add_argument('-l', '--loglevel', '--log-level',
                        help='Logging verbosity level threshold (to stderr)',
                        default='info')
    parser.add_argument('terms',
                        metavar='term',
                        nargs='*',
                        help='Single query to perform '
                             '(mutually exclusive with -b and -i).')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)-15s %(levelname)s: %(message)s',
                        level=args.loglevel.upper())

    if args.i:
        if args.b:
            raise Exception(
                'batch mode (-b) cannot be specified for '
                'interactive client (-i)')
        if args.terms:
            raise Exception(
                'query terms cannot be specified on command line for '
                'interactive client (-i)')
        logging.info('starting interactive search client...')
        with SearchClientWrapper(args.host, args.port) as search_client:
            logging.info('note: query terms are delimited by tabs')
            logging.info('enter a blank query to exit')
            line = input('> ')
            while line:
                terms = line.split('\t')
                for (comm_id, score) in execute_search_query(search_client,
                                                             terms,
                                                             args.k):
                    if args.with_scores:
                        print('{}	{}'.format(comm_id, score))
                    else:
                        print(comm_id)
                line = input('> ')
    elif args.b:
        logging.info('starting batch non-interactive search client...')
        if args.terms:
            raise Exception(
                'query terms cannot be specified on command line for '
                'batch client (-b)')
        with SearchClientWrapper(args.host, args.port) as search_client:
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
        with SearchClientWrapper(args.host, args.port) as search_client:
            for (comm_id, score) in execute_search_query(search_client,
                                                         args.terms,
                                                         args.k):
                if args.with_scores:
                    print('{}	{}'.format(comm_id, score))
                else:
                    print(comm_id)


if __name__ == "__main__":
    main()
