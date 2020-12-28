#!/usr/bin/env python

'''
Convert Tweet file to Concrete Communications file.
'''
from __future__ import unicode_literals

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
from concrete.util import set_stdout_encoding

try:
    JSONDecodeError = json.JSONDecodeError
except AttributeError:
    JSONDecodeError = ValueError


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
        return json_str_to_concrete_bytes(tweet_str)
    except UnicodeDecodeError:
        return None
    except JSONDecodeError:
        return None


def json_str_to_validated_concrete_bytes_skip_bad_lines(tweet_str):
    try:
        return json_str_to_validated_concrete_bytes(tweet_str)
    except UnicodeDecodeError:
        return None
    except JSONDecodeError:
        return None


def main():
    set_stdout_encoding()

    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Read tweets formatted in the Twitter JSON API and write'
                    ' communications',
    )
    parser.set_defaults(num_proc=1, chunk_size=10000, log_interval=10000)
    parser.add_argument('tweet_path', type=str,
                        help='Input twitter JSON file path (- for stdin)')
    parser.add_argument('concrete_path', type=str,
                        help='Output concrete file path (- for stdout)')
    parser.add_argument('--log-interval', type=int,
                        help='log an info message every log-interval tweets')
    parser.add_argument('-l', '--loglevel', '--log-level',
                        help='Logging verbosity level threshold (to stderr)',
                        default='info')
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
    args = parser.parse_args()

    # Won't work on Windows
    tweet_path = '/dev/fd/0' if args.tweet_path == '-' else args.tweet_path
    concrete_path = (
        '/dev/fd/1' if args.concrete_path == '-' else args.concrete_path
    )

    if args.log_conf_path:
        with open(args.log_conf_path) as f:
            logging.config.dictConfig(json.load(f))
    else:
        logging.basicConfig(format='%(asctime)-15s %(levelname)s: %(message)s',
                            level=args.loglevel.upper())

    if args.tweet_path != '-' and mimetypes.guess_type(tweet_path)[1] == 'gzip':
        tweet_reader = gzip.open(tweet_path, 'rb')
    else:
        tweet_reader = open(tweet_path, 'rb')

    if args.catch_ioerror:
        def _catch(g):
            it = iter(g)
            while True:
                try:
                    x = next(it)
                    yield x
                except IOError:
                    return
                except EOFError:
                    return
        tweet_reader = _catch(tweet_reader)

    if args.skip_bad_lines:
        if args.skip_invalid_comms:
            map_func = json_str_to_validated_concrete_bytes_skip_bad_lines
        else:
            map_func = json_str_to_concrete_bytes_skip_bad_lines
    else:
        if args.skip_invalid_comms:
            map_func = json_str_to_validated_concrete_bytes
        else:
            map_func = json_str_to_concrete_bytes

    with open(concrete_path, 'wb') as writer:
        i = 0

        p = Pool(args.num_proc)
        for concrete_bytes in p.imap(map_func, tweet_reader,
                                     args.chunk_size):
            if concrete_bytes is not None:
                if (i + 1) % args.log_interval == 0:
                    logging.info('writing tweet %d...' % (i + 1))
                writer.write(concrete_bytes)
                i += 1


if __name__ == "__main__":
    main()
