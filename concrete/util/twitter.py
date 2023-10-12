"""Convert between JSON and Concrete representations of Tweets

The JSON fields used by the Twitter API are documented at:

  https://dev.twitter.com/overview/api/tweets
"""
from __future__ import unicode_literals

import json
import logging
import time
import pycountry
from datetime import datetime

from ..metadata.ttypes import AnnotationMetadata, CommunicationMetadata
from ..communication.ttypes import Communication
from ..language.ttypes import LanguageIdentification
from ..twitter.ttypes import (
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

from .concrete_uuid import AnalyticUUIDGeneratorFactory
from .metadata import datetime_to_timestamp


TOOL_NAME = "Python module concrete.util.twitter"
TWEET_TYPE = "Tweet"
ISO_LANGS = pycountry.languages
CREATED_AT_FORMAT = '%a %b %d %H:%M:%S +0000 %Y'


def json_tweet_object_to_Communication(tweet):
    """Convert deserialized JSON Tweet object to :class:`.Communication`

    Args:
        tweet (object): Object created by deserializing a JSON Tweet string

    Returns:
        Communication: Communication representing the Tweet, with
        `tweetInfo` and `text` fields set (among others) but with
        a null (None) `sectionList`.
    """
    tweet_info = json_tweet_object_to_TweetInfo(tweet)

    augf = AnalyticUUIDGeneratorFactory()
    aug = augf.create()
    if 'id_str' in tweet:
        tweet_id = tweet['id_str']
    else:
        logging.warning('Tweet has no id_str, leaving communication id blank')
        tweet_id = None
    tweet_time = datetime_to_timestamp(datetime.strptime(tweet_info.createdAt,
                                                         CREATED_AT_FORMAT))
    comm = Communication(
        communicationMetadata=CommunicationMetadata(
            tweetInfo=tweet_info),
        metadata=AnnotationMetadata(
            tool=TOOL_NAME,
            timestamp=int(time.time())),
        originalText=json.dumps(tweet),
        text=tweet_info.text,
        type=TWEET_TYPE,
        uuid=next(aug),
        startTime=tweet_time,
        endTime=tweet_time,
        id=tweet_id
    )

    # either this, or pass in gen as parameter to fx
    # latter is more annoying to test but slightly cleaner
    if tweet_info.lid is not None:
        tweet_info.lid.uuid = next(aug)
        lidList = [tweet_info.lid]
        comm.lidList = lidList
    return comm


def snake_case_to_camelcase(value):
    """Converts snake case to camel case

    Implementation copied from this Stack Overflow post:
    http://goo.gl/SSgo9k

    Args:
        value (str): snake case (lower case with underscores) value

    Returns:
        str: camel case string corresponding to value (with isolated
        unscores stripped and sequences of two or more underscores
        reduced by one underscore)
    """
    def camelcase():
        yield lambda c: c.lower()
        while True:
            yield lambda c: c.capitalize()
    c = iter(camelcase())
    return u"".join(next(c)(x) if x else u'_' for x in value.split(u"_"))


def json_tweet_object_to_TweetInfo(tweet):
    """Create :class:`.TweetInfo` object from deserialized JSON Tweet
    object

    Args:
        tweet (dict): Object created by deserializing a JSON Tweet
            string

    Returns:
        TweetInfo: concrete object representing twitter metadata from
        tweet
    """

    def set_flat_fields(concrete_object, twitter_dict):
        """Copy data from the dictionary for the Twitter object to the
        corresponding Concrete data structure, ignoring nested
        data structures.

        The Twitter API uses snake_case for field names while the Concrete
        schema uses CamelCase for the same fields.

        Args:
            concrete_object (object): concrete object whose fields will
                be set according to the content in twitter_dict;
                will be modified
            twitter_dict (dict): twitter object (dictionary) whose
                entries will be used to set fields on concrete_object
        """
        for key in twitter_dict.keys():
            if not isinstance(twitter_dict[key], dict):
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

    if u'retweeted_status' in tweet and tweet[u'retweeted_status']:
        tweet_info.retweetedStatusId = tweet[u'retweeted_status']['id']
        tweet_info.retweetedUserId = tweet[u'retweeted_status']['user']['id']
        tweet_info.retweetedScreenName = tweet[u'retweeted_status']['user'][
            'screen_name'
        ]

    if u'entities' in tweet and tweet[u'entities']:
        twitter_entities = TwitterEntities()
        if tweet[u'entities'][u'hashtags']:
            twitter_entities.hashtagList = []
            for hashtag_dict in tweet[u'entities'][u'hashtags']:
                hashtag = HashTag()
                set_flat_fields(hashtag, hashtag_dict)
                hashtag.startOffset = hashtag_dict[u'indices'][0]
                hashtag.endOffset = hashtag_dict[u'indices'][1]
                twitter_entities.hashtagList.append(hashtag)
        if tweet[u'entities'][u'urls']:
            twitter_entities.urlList = []
            for url_dict in tweet[u'entities'][u'urls']:
                url = URL()
                set_flat_fields(url, url_dict)
                url.startOffset = url_dict[u'indices'][0]
                url.endOffset = url_dict[u'indices'][1]
                twitter_entities.urlList.append(url)
        if tweet[u'entities'][u'user_mentions']:
            twitter_entities.userMentionList = []
            for user_mention_dict in tweet[u'entities'][u'user_mentions']:
                user_mention = UserMention()
                set_flat_fields(user_mention, user_mention_dict)
                user_mention.startOffset = user_mention_dict[u'indices'][0]
                user_mention.endOffset = user_mention_dict[u'indices'][1]
                twitter_entities.userMentionList.append(user_mention)
        tweet_info.entities = twitter_entities

    if u'coordinates' in tweet and tweet[u'coordinates']:
        tweet_coordinates = TwitterCoordinates()
        tweet_coordinates.type = tweet[u'coordinates']['type']
        tweet_coordinates.coordinates = TwitterLatLong(
            longitude=tweet[u'coordinates'][u'coordinates'][0],
            latitude=tweet[u'coordinates'][u'coordinates'][1])
        tweet_info.coordinates = tweet_coordinates

    if u'place' in tweet and tweet[u'place']:
        twitter_place = TwitterPlace()
        set_flat_fields(twitter_place, tweet[u'place'])
        if tweet[u'place'][u'bounding_box']:
            bounding_box = BoundingBox()
            bb_dict = tweet[u'place'][u'bounding_box']
            set_flat_fields(bounding_box, bb_dict)
            if bounding_box.coordinateList is None:
                bounding_box.coordinateList = []
            if u'coordinates' in bb_dict and bb_dict[u'coordinates']:
                for [longitude, latitude] in bb_dict[u'coordinates'][0]:
                    bounding_box.coordinateList.append(TwitterLatLong(
                        longitude=longitude,
                        latitude=latitude))
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
    """Convert JSON Tweet string to Communication

    Args:
        json_tweet_string (str): JSON Tweet string from Twitter API
        check_empty (bool): If `True`, check if `json_tweet_string` is empty
            (return None if it is)
        check_delete (bool): If `True`, check for presence of `delete` field
            in Tweet JSON, and if the 'delete' field is present, return `None`

    Returns:
        Communication: Communication representing the Tweet, with
        `tweetInfo` and `text` fields set (among others) but with
        a null (None) `sectionList`.
    """

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
    """Create :class:`.TweetInfo` object from JSON Tweet string

    Args:
        json_tweet_string (str): JSON Tweet string from Twitter API

    Returns:
        TweetInfo: concrete twitter metadata object with fields
        set from json_tweet_string
    """
    tweet = json.loads(json_tweet_string)
    return json_tweet_object_to_TweetInfo(tweet)


def capture_tweet_lid(tweet):
    """
    Reads the `lang` field from a tweet from the twitter API, if it
    exists, and return corresponding concrete
    :class:`LanguageIdentification` object.

    Args:
        tweet (dict): Object created by deserializing a JSON Tweet string

    Returns:
        :class:`.LanguageIdentification` object, or None
        if the `lang` field is not present in the Tweet JSON
    """
    if u'lang' in tweet:
        amd = AnnotationMetadata(tool="Twitter LID",
                                 timestamp=int(time.time()),
                                 kBest=1)
        kvs = {}
        kvs[twitter_lid_to_iso639_3(tweet[u'lang'])] = 1.0
        return LanguageIdentification(metadata=amd,
                                      languageToProbabilityMap=kvs)
    else:
        return None


def twitter_lid_to_iso639_3(twitter_lid):
    """Convert Twitter Language ID string to ISO639-3 code

    Ref:
        https://developer.twitter.com/en/docs/developer-utilities/supported-languages/api-reference/get-help-languages

    Args:
        twitter_lid (str): This can be an iso639-3 code (no-op),
            iso639-1 2-letter abbr (converted to 3), or combo
            (split by '-', then first part converted)

            Per the Twitter documentation, "The language code may be
            formatted as ISO 639-1 alpha-2 (en), ISO 639-3 alpha-3
            (msa), or ISO 639-1 alpha-2 combined with an ISO 3166-1
            alpha-2 localization (zh-tw)."

    Returns:
        str: the ISO639-3 code corresponding to twitter_lid

    """
    def _iso639_1_to_iso639_3(iso639_1):
        if iso639_1 == 'in':
            return ISO_LANGS.get(alpha_2='id').alpha_3

        try:
            # pycountry 18.12.8 changed the behavior of pycountry.languages.get().
            # Prior versions raised a KeyError if the language was not found, but
            # starting with pycountry 18.12.8, None is returned instead:
            #   https://pypi.org/project/pycountry/18.12.8/
            iso_lang = ISO_LANGS.get(alpha_2=iso639_1)
            if iso_lang:
                return iso_lang.alpha_3
            else:
                return 'und'
        except KeyError:
            # As of early 2018, Twitter is (at least sometimes) using
            # the incorrect ISO-639-1 language code for Indonesian.
            #
            # This issue was acknowledged by Twitter tech support in this
            # 2015 forum post:
            #   https://twittercommunity.com/t/hebrew-and-indonesian-getting-incorrect-lang-codes/13044/3
            #
            # The 2015 forum post mentions that Twitter is using the incorrect
            # language code for both Hebrew and Indonesian, but as of 2018
            # Twitter is using the correct ISO-639-1 code for Hebrew.
            #
            # The list of Twitter language codes (including the incorrect
            # Indonesian code) could be found here:
            #   https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/premium-operators
            #   http://support.gnip.com/sources/twitter/powertrack_operators.html
            # The ISO-639-1 character codes are correct for all 60+ languages currently
            # supported by Twitter, except for Indonesian.
            return 'und'

    if len(twitter_lid) == 2:
        return _iso639_1_to_iso639_3(twitter_lid)
    elif twitter_lid.find('-') == 2 and len(twitter_lid) == 5:
        return _iso639_1_to_iso639_3(twitter_lid[0:2])
    else:
        return twitter_lid
