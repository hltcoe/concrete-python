#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals

from time import sleep, time
import argparse
import logging
import sys

import concrete.version
import concrete.util
from concrete.util import set_stdout_encoding


def main():
    set_stdout_encoding()

    parser = argparse.ArgumentParser(
        description='Wait for a service to come up.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('service_name',
                        choices=[
                            'FetchCommunication',
                            'StoreCommunication',
                            'AnnotateCommunication',
                            'ActiveLearnerClient',
                            'ActiveLearnerServer',
                            'ResultsServer',
                            'Search',
                            'SearchProxy',
                            'Feedback',
                            'Summarization',
                        ],
                        help='name of service to wait for')
    parser.add_argument('--host', help='hostname to serve on',
                        default='localhost')
    parser.add_argument('--port', type=int, help='port to serve on',
                        default=9090)
    parser.add_argument('--sleep-interval', type=int, default=5)
    parser.add_argument('--timeout', type=int,
                        help='Default: no timeout')
    parser.add_argument('-l', '--loglevel',
                        help='Logging verbosity level threshold (to stderr)',
                        default='info')
    concrete.version.add_argparse_argument(parser)
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)-15s %(levelname)s: %(message)s',
                        level=args.loglevel.upper())

    cli_wrapper_class = getattr(concrete.util,
                                args.service_name + 'ClientWrapper')

    logging.info('waiting for {} service at {}:{} to come up'.format(
        args.service_name, args.host, args.port))
    start = time()
    alive = False
    while not alive:
        try:
            with cli_wrapper_class(args.host, args.port) as cli:
                if cli.alive():
                    alive = True
                    break
        except:
            pass
        if args.timeout is not None and time() - start > args.timeout:
            logging.info('timed out after {}s'.format(args.timeout))
            break
        else:
            logging.info('waiting {}s for {} service to come up'.format(
                args.sleep_interval, args.service_name))
            sleep(args.sleep_interval)

    if alive:
        logging.info('{} service at {}:{} is up'.format(
            args.service_name, args.host, args.port))
    else:
        logging.error('{} service at {}:{} is down'.format(
            args.service_name, args.host, args.port))
        sys.exit(1)


if __name__ == "__main__":
    main()
