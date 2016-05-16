"""Convert between JSON and Concrete representations of Tweets

The fields used by the Twitter API are documented at:

  https://dev.twitter.com/overview/api/tweets
"""

import json
import logging
import time

from concrete import (
    AnnotationMetadata,
    BoundingBox,
    Communication,
    CommunicationMetadata,
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

from concrete.util.concrete_uuid import AnalyticUUIDGeneratorFactory


TOOL_NAME = "Python module concrete.util.twitter"
TWEET_TYPE = "Tweet"


def json_tweet_object_to_Communication(tweet):
    """
    """
    tweet_info = json_tweet_object_to_TweetInfo(tweet)

    augf = AnalyticUUIDGeneratorFactory()
    aug = augf.create()
    if 'id_str' in tweet:
        tweet_id = tweet['id_str']
    else:
        logging.warning('Tweet has no id_str, leaving communication id blank')
        tweet_id = None
    comm = Communication(
        communicationMetadata=CommunicationMetadata(
            tweetInfo=tweet_info),
        metadata=AnnotationMetadata(
            tool=TOOL_NAME,
            timestamp=int(time.time())),
        originalText=tweet_info.text,
        text=tweet_info.text,
        type=TWEET_TYPE,
        uuid=aug.next(),
        id=tweet_id
    )

    return comm


def json_tweet_object_to_TweetInfo(tweet):
    """
    Args:

    Returns:
    """
    def snake_case_to_camelcase(value):
        """Implementation copied from: http://goo.gl/SSgo9k
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
                    logging.debug("Concrete schema for '%s' missing field "
                                  "for Twitter API field '%s'" %
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

        if tweet[u'coordinates']:
            tweet_coordinates = TwitterCoordinates()
            tweet_coordinates.type = tweet[u'coordinates']['type']
            tweet_coordinates.coordinates = TwitterLatLong(
                latitude=tweet[u'coordinates'][u'coordinates'][0],
                longitude=tweet[u'coordinates'][u'coordinates'][1])
            tweet_info.coordinates = tweet_coordinates

        if tweet[u'place']:
            twitter_place = TwitterPlace()
            set_flat_fields(twitter_place, tweet[u'place'])
            if tweet[u'place'][u'bounding_box']:
                bounding_box = BoundingBox()
                set_flat_fields(bounding_box, tweet[u'place'][u'bounding_box'])
                if bounding_box.coordinateList is None:
                    bounding_box.coordinateList = []
                twitter_place.boundingBox = bounding_box
            if tweet[u'place'][u'attributes']:
                place_attributes = PlaceAttributes()
                set_flat_fields(place_attributes,
                                tweet[u'place'][u'attributes'])
                twitter_place.attributes = place_attributes
            tweet_info.place = twitter_place

    return tweet_info


def json_tweet_string_to_Communication(json_tweet_string, check_empty=False,
                                       check_delete=False):
    json_tweet_string = json_tweet_string.strip()
    if (not check_empty) or json_tweet_string:
        json_tweet = json.loads(json_tweet_string)
        if (not check_delete) or tuple(json_tweet.keys()) != ('delete',):
            return json_tweet_object_to_Communication(json_tweet)
        else:
            return None
    else:
        return None


def json_tweet_string_to_TweetInfo(json_tweet_string):
    tweet = json.loads(json_tweet_string)
    return json_tweet_object_to_TweetInfo(tweet)
