"""Convert between JSON and Concrete representations of Tweets

The fields used by the Twitter API are documented at:

  https://dev.twitter.com/overview/api/tweets
"""

import json
import logging
import time
import pycountry
from datetime import datetime

from concrete import (
    AnnotationMetadata,
    BoundingBox,
    Communication,
    CommunicationMetadata,
    HashTag,
    LanguageIdentification,
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
ISO_LANGS = pycountry.languages
CREATED_AT_FORMAT = '%a %b %d %H:%M:%S +0000 %Y'
EPOCH = datetime.utcfromtimestamp(0)


def unix_time(dt):
    '''
    Source:
    http://stackoverflow.com/questions/6999726/how-can-i-convert-a-datetime-object-to-milliseconds-since-epoch-unix-time-in-p
    '''
    return int((dt - EPOCH).total_seconds())


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
    tweet_time = unix_time(datetime.strptime(tweet_info.createdAt,
                                             CREATED_AT_FORMAT))
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
        startTime=tweet_time,
        endTime=tweet_time,
        id=tweet_id
    )

    # either this, or pass in gen as parameter to fx
    # latter is more annoying to test but slightly cleaner
    if tweet_info.lid is not None:
        tweet_info.lid.uuid = aug.next()
        lidList = [tweet_info.lid]
        comm.lidList = lidList
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
    json_twitter_user = tweet[u'user']
    set_flat_fields(twitter_user, json_twitter_user)
    if json_twitter_user['lang']:
        twitter_lid = json_twitter_user['lang']
        twitter_user.lang = twitter_lid_to_iso639_3(twitter_lid)
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

    tweet_info.lid = capture_tweet_lid(tweet)
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


def capture_tweet_lid(twitter_dict):
    """
    Attempts to capture the 'lang' field in the twitter API, if it
    exists.

    Returns a list of LanguageIdentification objects, or None if the
    field is not present in the tweet json.
    """
    if u'lang' in twitter_dict:
        amd = AnnotationMetadata(tool="Twitter LID",
                                 timestamp=int(time.time()),
                                 kBest=1)
        kvs = {}
        kvs[twitter_lid_to_iso639_3(twitter_dict[u'lang'])] = 1.0
        return LanguageIdentification(metadata=amd,
                                      languageToProbabilityMap=kvs)
    else:
        return None


def twitter_lid_to_iso639_3(twitter_lid):
    """
    Ref: https://dev.twitter.com/rest/reference/get/help/languages

    This can be an iso639-3 code (no-op), iso639-1 2-letter abbr
    (converted to 3), or combo (split by '-', then first part converted)
    """
    if len(twitter_lid) == 2:
        return ISO_LANGS.get(iso639_1_code=twitter_lid).iso639_3_code
    elif '-' in twitter_lid and len(twitter_lid) == 5:
        spl = twitter_lid[0:2]
        return ISO_LANGS.get(iso639_1_code=spl).iso639_3_code
    else:
        return twitter_lid
