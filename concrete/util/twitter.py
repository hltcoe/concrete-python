"""Convert between JSON and Concrete representations of Tweets

The fields used by the Twitter API are documented at:

  https://dev.twitter.com/overview/api/tweets
"""

import json
import logging
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
                camelcased_key = snake_case_to_camelcase(key)
                if hasattr(concrete_object, camelcased_key):
                    setattr(concrete_object, camelcased_key, twitter_dict[key])
                else:
                    logging.warn("Concrete schema for '%s' missing field for Twitter API field '%s'" %
                                 (type(concrete_object), key))

    tweet_info = TweetInfo()
    set_flat_fields(tweet_info, tweet)

    twitter_user = TwitterUser()
    set_flat_fields(twitter_user, tweet[u'user'])
    tweet_info.user = twitter_user

    if tweet[u'entities']:
        twitter_entities = TwitterEntities()
        if tweet[u'entities'][u'hashtags']:
            twitter_entities.hashtagList = []
            for hashtag_dict in tweet[u'entities'][u'hashtags']:
                hashtag = HashTag()
                set_flat_fields(hashtag, hashtag_dict)
                twitter_entities.hashtagList.append(hashtag)
        if tweet[u'entities'][u'urls']:
            twitter_entities.urlList = []
            for url_dict in tweet[u'entities'][u'urls']:
                url = URL()
                set_flat_fields(url, url_dict)
                twitter_entities.urlList.append(url)
        if tweet[u'entities'][u'user_mentions']:
            twitter_entities.userMentionList = []
            for user_mention_dict in tweet[u'entities'][u'user_mentions']:
                user_mention = UserMention()
                set_flat_fields(user_mention, user_mention_dict)
                twitter_entities.userMentionList.append(user_mention)
        tweet_info.entities = twitter_entities

    return tweet_info


def json_tweet_string_to_TweetInfo(tweet_json_string):
    tweet = json.loads(tweet_json_string)
    return json_tweet_object_to_TweetInfo(tweet)
