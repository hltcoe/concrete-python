#!/usr/bin/env python

"""
Deprecated: use tweets2concrete instead
Convert Tweet file to Concrete Communications file.
"""

import argparse
import codecs
import gzip
import logging
import mimetypes

from concrete.util import CommunicationWriter
from concrete.util.twitter import json_tweet_string_to_Communication


def main():
    logging.basicConfig(
        format='%(levelname)7s:  %(message)s', level=logging.WARNING)
    logging.warning(
        'tweets2concrete.py is deprecated: use tweets2concrete instead')

    parser = argparse.ArgumentParser(description="")
    parser.add_argument('tweet_file')
    parser.add_argument('concrete_file')
    args = parser.parse_args()

    if mimetypes.guess_type(args.tweet_file)[1] == 'gzip':
        gz_file = gzip.open(args.tweet_file, 'r')
        utf8_reader = codecs.getreader("utf-8")
        tweet_reader = utf8_reader(gz_file)
    else:
        tweet_reader = codecs.open(args.tweet_file, 'r', encoding='utf-8')

    comm_writer = CommunicationWriter()
    comm_writer.open(args.concrete_file)

    for tweet in tweet_reader:
        tweet = tweet.strip()

        # Ignore empty lines and deleted Tweets
        if tweet and u'{"delete":{"status":' not in tweet:
            comm = json_tweet_string_to_Communication(tweet)
            comm_writer.write(comm)

    comm_writer.close()


if __name__ == "__main__":
    main()
