#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging

from boto import connect_s3
import concrete.version
from concrete.util import (
    CommunicationReader, FileType, set_stdout_encoding, S3BackedStoreHandler,
    DEFAULT_S3_KEY_PREFIX_LEN,
)


def main():
    set_stdout_encoding()

    parser = argparse.ArgumentParser(
        description='Read communications from file and write to an AWS S3 '
                    'bucket (keyed by communication id).',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('input_path',
                        help='path to input communications (uncompressed, '
                             'gz, bz2, tar, zip, etc.) (if "-", read from '
                             'stdin)')
    parser.add_argument('bucket_name', help='name of S3 bucket to write to')
    parser.add_argument('--prefix-len', type=int, default=DEFAULT_S3_KEY_PREFIX_LEN,
                        help='S3 keys are prefixed with hashes of this length')
    parser.add_argument('-l', '--loglevel',
                        help='Logging verbosity level threshold (to stderr)',
                        default='info')
    concrete.version.add_argparse_argument(parser)
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)-15s %(levelname)s: %(message)s',
                        level=args.loglevel.upper())

    # if input_path is '-', read from stdin
    if args.input_path == '-':
        pairs = CommunicationReader('/dev/fd/0', filetype=FileType.STREAM)
    else:
        pairs = CommunicationReader(args.input_path)

    logging.info('connecting to s3')
    conn = connect_s3()
    logging.info('retrieving bucket {}'.format(args.bucket_name))
    bucket = conn.get_bucket(args.bucket_name)
    logging.info('reading from {}; writing to s3 bucket {}, prefix length {}'.format(
        args.input_path, args.bucket_name, args.prefix_len))
    handler = S3BackedStoreHandler(bucket, args.prefix_len)
    for (comm, _) in pairs:
        logging.info('storing {}'.format(comm.id))
        handler.store(comm)


if __name__ == "__main__":
    main()
