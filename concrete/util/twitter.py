"""Convert between JSON and Concrete representations of Tweets

The fields used by the Twitter API are documented at:

  https://dev.twitter.com/overview/api/tweets
"""

import json
import re

from concrete import (
    BoundingBox,
    HashTag,
    PlaceAttributes,
    TweetInfo,
    TwitterCoordinates,
    TwitterEntities,
    TwitterLatLong,
    TwitterPlace,
    TwitterUser,
    URL,
    UserMention
)


def json_tweet_object_to_TweetInfo(tweet):
    """
    """
    def snake_case_to_camelcase(value):
        """Implementation copied from:

             http://stackoverflow.com/questions/4303492/how-can-i-simplify-this-conversion-from-underscore-to-camelcase-in-python
        """
        def camelcase():
            yield unicode.lower
            while True:
                yield unicode.capitalize
        c = camelcase()
        return u"".join(c.next()(x) if x else u'_' for x in value.split(u"_"))

    def set_flat_fields(concrete_object, twitter_dict):
        """Copy data from the dictionary for the Twitter object to the
        corresponding Concrete data structure, ignoring nested
        data structures.

        The Twitter API uses snake_case for field names while the Concrete
        schema uses CamelCase for the same fields.
        """
        for key in twitter_dict.keys():
            if type(twitter_dict[key]) != dict:
                setattr(concrete_object, snake_case_to_camelcase(key), twitter_dict[key])

    twitter_user = TwitterUser()
    set_flat_fields(twitter_user, tweet[u'user'])

    tweet_info = TweetInfo()
    set_flat_fields(tweet_info, tweet)
    tweet_info.user = twitter_user

    return tweet_info


def json_tweet_string_to_TweetInfo(tweet_json_string):
    tweet = json.loads(tweet_json_string)
    return json_tweet_object_to_TweetInfo(tweet)
