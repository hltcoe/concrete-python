#!/usr/bin/env python

'''
Convert Tweet file to Concrete Communications file.
'''

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from multiprocessing import Pool
import gzip
import json
import logging
import logging.config
import mimetypes

import concrete.version
from concrete.validate import validate_communication
from concrete.util.mem_io import write_communication_to_buffer
from concrete.util.twitter import json_tweet_string_to_Communication


def json_str_to_validated_concrete_bytes(tweet_str):
    tweet_str = tweet_str.decode('utf-8')
    b = json_tweet_string_to_Communication(tweet_str, True, True)
    if b is None or not validate_communication(b):
        return None
    else:
        return write_communication_to_buffer(b)


def json_str_to_concrete_bytes(tweet_str):
    tweet_str = tweet_str.decode('utf-8')
    b = json_tweet_string_to_Communication(tweet_str, True, True)
    if b is None:
        return None
    else:
        return write_communication_to_buffer(b)


def json_str_to_concrete_bytes_skip_bad_lines(tweet_str):
    try:
        tweet_str = tweet_str.decode('utf-8')
        return json_str_to_concrete_bytes(tweet_str)
    except:
        return None


def json_str_to_validated_concrete_bytes_skip_bad_lines(tweet_str):
    try:
        tweet_str = tweet_str.decode('utf-8')
        return json_str_to_concrete_bytes(tweet_str)
    except:
        return None


def main():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Read tweets formatted in the Twitter JSON API and write'
                    ' communications',
    )
    parser.set_defaults(log_level='INFO', num_proc=1, chunk_size=10000,
                        log_interval=10000)
    parser.add_argument('tweet_path', type=str,
                        help='Input twitter JSON file path (- for stdin)')
    parser.add_argument('concrete_path', type=str,
                        help='Output concrete file path (- for stdout)')
    parser.add_argument('--log-interval', type=int,
                        help='log an info message every log-interval tweets')
    parser.add_argument('--log-level', type=str,
                        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR'),
                        help='Logging verbosity level (to stderr)')
    parser.add_argument('--log-conf-path', type=str,
                        help='Path to log config file (overrides log-level).'
                             ' Format is json encoding of logging.config'
                             ' dictConfig schema: https://docs.python.org/2/'
                             'library/logging.config.html#'
                             'logging-config-dictschema')
    parser.add_argument('--num-proc', type=int,
                        help='Number of worker processes to use')
    parser.add_argument('--chunk-size', type=int,
                        help='Chunk size (in number of tweets) when'
                             ' dispatching jobs to workers')
    parser.add_argument('--catch-ioerror', action='store_true',
                        help='Treat IOError as successful end of stream'
                             ' (recommended if gzipped input files were not'
                             ' completely written)')
    parser.add_argument('--skip-bad-lines', action='store_true',
                        help='Skip malformatted json lines'
                             ' (by default, they crash the program)')
    parser.add_argument('--skip-invalid-comms', action='store_true',
                        help='Skip invalid communications (increases runtime)'
                             ' (by default, validation is not performed)')
    concrete.version.add_argparse_argument(parser)
    ns = parser.parse_args()

    # Won't work on Windows... but that use case is very unlikely
    tweet_path = '/dev/fd/0' if ns.tweet_path == '-' else ns.tweet_path
    concrete_path = (
        '/dev/fd/1' if ns.concrete_path == '-' else ns.concrete_path
    )

    if ns.log_conf_path:
        with open(ns.log_conf_path) as f:
            logging.config.dictConfig(json.load(f))
    else:
        logging.basicConfig(
            level=ns.log_level,
            format='%(asctime)-15s %(levelname)s: %(message)s'
        )

    if ns.tweet_path != '-' and mimetypes.guess_type(tweet_path)[1] == 'gzip':
        tweet_reader = gzip.open(tweet_path, 'r')
    else:
        tweet_reader = open(tweet_path, 'rb')

    if ns.catch_ioerror:
        def _catch(g):
            it = iter(g)
            while True:
                try:
                    x = it.next()
                    yield x
                except IOError:
                    raise StopIteration('Caught IOError.')
        tweet_reader = _catch(tweet_reader)

    if ns.skip_bad_lines:
        if ns.skip_invalid_comms:
            map_func = json_str_to_validated_concrete_bytes_skip_bad_lines
        else:
            map_func = json_str_to_concrete_bytes_skip_bad_lines
    else:
        if ns.skip_invalid_comms:
            map_func = json_str_to_validated_concrete_bytes
        else:
            map_func = json_str_to_concrete_bytes

    with open(concrete_path, 'wb') as writer:
        i = 0

        p = Pool(ns.num_proc)
        for concrete_bytes in p.imap(map_func, tweet_reader,
                                     ns.chunk_size):
            if concrete_bytes is not None:
                if (i + 1) % ns.log_interval == 0:
                    logging.info('writing tweet %d...' % (i + 1))
                writer.write(concrete_bytes)
                i += 1


if __name__ == "__main__":
    main()
