#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging

from boto import connect_s3
import concrete.version
from concrete.util import (
    CommunicationWriterTGZ, set_stdout_encoding,
    S3BackedCommunicationContainer
)


def main():
    set_stdout_encoding()

    parser = argparse.ArgumentParser(
        description='Read communications from AWS S3 bucket (keyed by '
                    'communication id) and write to a tar.gz file.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('bucket_name', help='name of S3 bucket to read from')
    parser.add_argument('output_path',
                        help='path to input communications (uncompressed, '
                             'gz, bz2, tar, zip, etc.)')
    parser.add_argument('--prefix',
                        help='fetch only those keys starting with this prefix')
    parser.add_argument('-l', '--loglevel',
                        help='Logging verbosity level threshold (to stderr)',
                        default='info')
    concrete.version.add_argparse_argument(parser)
    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)7s:  %(message)s', level=args.loglevel.upper())

    logging.info('connecting to s3')
    conn = connect_s3()
    logging.info('retrieving bucket {}'.format(args.bucket_name))
    bucket = conn.get_bucket(args.bucket_name)
    if args.prefix:
        logging.info('reading from s3 bucket {}, prefix {}, and writing to {}'.format(
            args.bucket_name, args.prefix, args.output_path))
    else:
        logging.info('reading from s3 bucket {} and writing to {}'.format(
            args.bucket_name, args.output_path))
    container = S3BackedCommunicationContainer(bucket, args.prefix)
    with CommunicationWriterTGZ(args.output_path) as writer:
        for comm_id in container:
            logging.info('fetching {}'.format(comm_id))
            writer.write(container[comm_id])


if __name__ == "__main__":
    main()
