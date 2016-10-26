from pytest import fixture

from concrete.util.twitter import (json_tweet_object_to_Communication,
                                   twitter_lid_to_iso639_3)


TWEET_TXT = ("Barber tells me - his son is colorblind / my hair is auburn /"
             " and auburn is a shade of green")

TWEET_ID = 238426131689242624
TWEET_ID_STR = u'238426131689242624'

RT_TWEET_TXT = 'Barber tells me'

RT_TWEET_ID = 238426131689242623
RT_TWEET_ID_STR = u'238426131689242623'

REPLY_TWEET_ID = 238426131689242622
REPLY_TWEET_ID_STR = u'238426131689242622'


@fixture
def tweet():
    return {u'text': TWEET_TXT,
            u'id_str': TWEET_ID_STR,
            u'id': TWEET_ID,
            u'created_at': 'Wed Aug 27 13:08:45 +0000 2008',
            u'user': {u'screen_name': 'charman',
                      u'name': 'C Harman',
                      u'lang': 'ja',
                      u'verified': False,
                      u'id': 1234,
                      u'id_str': '1234'},
            u'entities': {u'symbols': [],
                          u'hashtags': [{u'indices': [32, 36],
                                         u'text': u'lol'}],
                          u'user_mentions': [],
                          u'urls': []},
            u'coordinates': {u'coordinates': [-75.5, 40.25],
                             u'type': u'Point'},
            u'place': {u'attributes': {},
                       u'bounding_box': {u'coordinates': [[[-77.25, 38.5],
                                                           [-76.0, 38.5],
                                                           [-76.0, 38.125],
                                                           [-77.25, 38.125]]],
                                         u'type': u'Polygon'},
                       u'country': u'United States',
                       u'country_code': u'US',
                       u'full_name': u'Washington, DC',
                       u'id': u'01fbe706f872cb32',
                       u'name': u'Washington',
                       u'place_type': u'city',
                       u'url': u'http://api.twitter.com/1/geo/id/'
                               u'01fbe706f872cb32.json'},
            u'retweeted_status': {u'text': RT_TWEET_TXT,
                                  u'id_str': RT_TWEET_ID_STR,
                                  u'id': RT_TWEET_ID,
                                  u'created_at': 'Wed Aug 27 13:08:44 +0000 '
                                                 '2008',
                                  u'user': {u'screen_name': 'charman2',
                                            u'name': 'C Harman 2',
                                            u'lang': 'ja',
                                            u'verified': False,
                                            u'id': 1235,
                                            u'id_str': '1235'},
                                  u'entities': {u'symbols': [],
                                                u'hashtags': [],
                                                u'user_mentions': [],
                                                u'urls': []}},
            u'in_reply_to_status_id': REPLY_TWEET_ID,
            u'in_reply_to_status_id_str': REPLY_TWEET_ID_STR,
            u'in_reply_to_screen_name': 'charman3',
            u'in_reply_to_user_id': 1236,
            u'in_reply_to_user_id_str': u'1236',
            u'lang': u'en'}


def test_twitter_lid_conversion():
    assert 'eng' == twitter_lid_to_iso639_3('en-gb')
    assert 'msa' == twitter_lid_to_iso639_3('msa')
    assert 'hun' == twitter_lid_to_iso639_3('hu')
    assert 'zho' == twitter_lid_to_iso639_3('zh-cn')
    assert 'zho' == twitter_lid_to_iso639_3('zh-tw')
    assert 'und' == twitter_lid_to_iso639_3('und')
    assert 'eng' == twitter_lid_to_iso639_3('eng')


def test_json_tweet_object_to_Communication(tweet):
    comm = json_tweet_object_to_Communication(tweet)
    tweet_info = comm.communicationMetadata.tweetInfo

    assert TWEET_ID_STR == comm.id
    assert TWEET_TXT == comm.text
    assert 1219842525 == comm.startTime
    assert 1219842525 == comm.endTime

    assert TWEET_ID == tweet_info.id
    assert 'jpn' == tweet_info.user.lang
    assert 'charman' == tweet_info.user.screenName
    assert 'C Harman' == tweet_info.user.name
    assert 1234 == tweet_info.user.id

    assert RT_TWEET_ID == tweet_info.retweetedStatusId
    assert 1235 == tweet_info.retweetedUserId
    assert 'charman2' == tweet_info.retweetedScreenName

    assert REPLY_TWEET_ID == tweet_info.inReplyToStatusId
    assert 1236 == tweet_info.inReplyToUserId
    assert 'charman3' == tweet_info.inReplyToScreenName

    assert 1 == len(tweet_info.entities.hashtagList)
    assert u'lol' == tweet_info.entities.hashtagList[0].text
    assert 32 == tweet_info.entities.hashtagList[0].startOffset
    assert 36 == tweet_info.entities.hashtagList[0].endOffset

    assert u'Point' == tweet_info.coordinates.type
    assert -75.5 == tweet_info.coordinates.coordinates.longitude
    assert 40.25 == tweet_info.coordinates.coordinates.latitude

    assert u'Polygon' == tweet_info.place.boundingBox.type
    assert -77.25 == tweet_info.place.boundingBox.coordinateList[0].longitude
    assert 38.5 == tweet_info.place.boundingBox.coordinateList[0].latitude
    assert -76.0 == tweet_info.place.boundingBox.coordinateList[1].longitude
    assert 38.5 == tweet_info.place.boundingBox.coordinateList[1].latitude
    assert -76.0 == tweet_info.place.boundingBox.coordinateList[2].longitude
    assert 38.125 == tweet_info.place.boundingBox.coordinateList[2].latitude
    assert -77.25 == tweet_info.place.boundingBox.coordinateList[3].longitude
    assert 38.125 == tweet_info.place.boundingBox.coordinateList[3].latitude
    assert u'United States' == tweet_info.place.country
    assert u'US' == tweet_info.place.countryCode
    assert u'Washington, DC' == tweet_info.place.fullName
    assert u'01fbe706f872cb32' == tweet_info.place.id
    assert u'Washington' == tweet_info.place.name
    assert u'city' == tweet_info.place.placeType
    assert u'http://api.twitter.com/1/geo/id/01fbe706f872cb32.json' == \
        tweet_info.place.url

    assert 1 == len(comm.lidList)
    kvm = comm.lidList[0].languageToProbabilityMap
    assert 'eng' == kvm.keys()[0]
    assert 1.0 == kvm['eng']


def test_json_tweet_object_to_Communication_missing_lid(tweet):
    del tweet['lang']

    comm = json_tweet_object_to_Communication(tweet)
    tweet_info = comm.communicationMetadata.tweetInfo

    assert TWEET_ID_STR == comm.id
    assert TWEET_TXT == comm.text
    assert 1219842525 == comm.startTime
    assert 1219842525 == comm.endTime

    assert TWEET_ID == tweet_info.id
    assert 'jpn' == tweet_info.user.lang
    assert 'charman' == tweet_info.user.screenName
    assert 'C Harman' == tweet_info.user.name
    assert 1234 == tweet_info.user.id

    assert RT_TWEET_ID == tweet_info.retweetedStatusId
    assert 1235 == tweet_info.retweetedUserId
    assert 'charman2' == tweet_info.retweetedScreenName

    assert REPLY_TWEET_ID == tweet_info.inReplyToStatusId
    assert 1236 == tweet_info.inReplyToUserId
    assert 'charman3' == tweet_info.inReplyToScreenName

    assert 1 == len(tweet_info.entities.hashtagList)
    assert u'lol' == tweet_info.entities.hashtagList[0].text
    assert 32 == tweet_info.entities.hashtagList[0].startOffset
    assert 36 == tweet_info.entities.hashtagList[0].endOffset

    assert u'Point' == tweet_info.coordinates.type
    assert -75.5 == tweet_info.coordinates.coordinates.longitude
    assert 40.25 == tweet_info.coordinates.coordinates.latitude

    assert u'Polygon' == tweet_info.place.boundingBox.type
    assert -77.25 == tweet_info.place.boundingBox.coordinateList[0].longitude
    assert 38.5 == tweet_info.place.boundingBox.coordinateList[0].latitude
    assert -76.0 == tweet_info.place.boundingBox.coordinateList[1].longitude
    assert 38.5 == tweet_info.place.boundingBox.coordinateList[1].latitude
    assert -76.0 == tweet_info.place.boundingBox.coordinateList[2].longitude
    assert 38.125 == tweet_info.place.boundingBox.coordinateList[2].latitude
    assert -77.25 == tweet_info.place.boundingBox.coordinateList[3].longitude
    assert 38.125 == tweet_info.place.boundingBox.coordinateList[3].latitude
    assert u'United States' == tweet_info.place.country
    assert u'US' == tweet_info.place.countryCode
    assert u'Washington, DC' == tweet_info.place.fullName
    assert u'01fbe706f872cb32' == tweet_info.place.id
    assert u'Washington' == tweet_info.place.name
    assert u'city' == tweet_info.place.placeType
    assert u'http://api.twitter.com/1/geo/id/01fbe706f872cb32.json' == \
        tweet_info.place.url

    assert comm.lidList is None


def test_json_tweet_object_to_Communication_missing_coordinates(tweet):
    del tweet['coordinates']

    comm = json_tweet_object_to_Communication(tweet)
    tweet_info = comm.communicationMetadata.tweetInfo

    assert TWEET_ID_STR == comm.id
    assert TWEET_TXT == comm.text
    assert 1219842525 == comm.startTime
    assert 1219842525 == comm.endTime

    assert TWEET_ID == tweet_info.id
    assert 'jpn' == tweet_info.user.lang
    assert 'charman' == tweet_info.user.screenName
    assert 'C Harman' == tweet_info.user.name
    assert 1234 == tweet_info.user.id

    assert RT_TWEET_ID == tweet_info.retweetedStatusId
    assert 1235 == tweet_info.retweetedUserId
    assert 'charman2' == tweet_info.retweetedScreenName

    assert REPLY_TWEET_ID == tweet_info.inReplyToStatusId
    assert 1236 == tweet_info.inReplyToUserId
    assert 'charman3' == tweet_info.inReplyToScreenName

    assert 1 == len(tweet_info.entities.hashtagList)
    assert u'lol' == tweet_info.entities.hashtagList[0].text
    assert 32 == tweet_info.entities.hashtagList[0].startOffset
    assert 36 == tweet_info.entities.hashtagList[0].endOffset

    assert tweet_info.coordinates is None

    assert u'Polygon' == tweet_info.place.boundingBox.type
    assert -77.25 == tweet_info.place.boundingBox.coordinateList[0].longitude
    assert 38.5 == tweet_info.place.boundingBox.coordinateList[0].latitude
    assert -76.0 == tweet_info.place.boundingBox.coordinateList[1].longitude
    assert 38.5 == tweet_info.place.boundingBox.coordinateList[1].latitude
    assert -76.0 == tweet_info.place.boundingBox.coordinateList[2].longitude
    assert 38.125 == tweet_info.place.boundingBox.coordinateList[2].latitude
    assert -77.25 == tweet_info.place.boundingBox.coordinateList[3].longitude
    assert 38.125 == tweet_info.place.boundingBox.coordinateList[3].latitude
    assert u'United States' == tweet_info.place.country
    assert u'US' == tweet_info.place.countryCode
    assert u'Washington, DC' == tweet_info.place.fullName
    assert u'01fbe706f872cb32' == tweet_info.place.id
    assert u'Washington' == tweet_info.place.name
    assert u'city' == tweet_info.place.placeType
    assert u'http://api.twitter.com/1/geo/id/01fbe706f872cb32.json' == \
        tweet_info.place.url

    assert 1 == len(comm.lidList)
    kvm = comm.lidList[0].languageToProbabilityMap
    assert 'eng' == kvm.keys()[0]
    assert 1.0 == kvm['eng']


def test_json_tweet_object_to_Communication_missing_place(tweet):
    del tweet['place']

    comm = json_tweet_object_to_Communication(tweet)
    tweet_info = comm.communicationMetadata.tweetInfo

    assert TWEET_ID_STR == comm.id
    assert TWEET_TXT == comm.text
    assert 1219842525 == comm.startTime
    assert 1219842525 == comm.endTime

    assert TWEET_ID == tweet_info.id
    assert 'jpn' == tweet_info.user.lang
    assert 'charman' == tweet_info.user.screenName
    assert 'C Harman' == tweet_info.user.name
    assert 1234 == tweet_info.user.id

    assert RT_TWEET_ID == tweet_info.retweetedStatusId
    assert 1235 == tweet_info.retweetedUserId
    assert 'charman2' == tweet_info.retweetedScreenName

    assert REPLY_TWEET_ID == tweet_info.inReplyToStatusId
    assert 1236 == tweet_info.inReplyToUserId
    assert 'charman3' == tweet_info.inReplyToScreenName

    assert 1 == len(tweet_info.entities.hashtagList)
    assert u'lol' == tweet_info.entities.hashtagList[0].text
    assert 32 == tweet_info.entities.hashtagList[0].startOffset
    assert 36 == tweet_info.entities.hashtagList[0].endOffset

    assert u'Point' == tweet_info.coordinates.type
    assert -75.5 == tweet_info.coordinates.coordinates.longitude
    assert 40.25 == tweet_info.coordinates.coordinates.latitude

    assert tweet_info.place is None

    assert 1 == len(comm.lidList)
    kvm = comm.lidList[0].languageToProbabilityMap
    assert 'eng' == kvm.keys()[0]
    assert 1.0 == kvm['eng']


def test_json_tweet_object_to_Communication_missing_retweeted_status(tweet):
    del tweet['retweeted_status']

    comm = json_tweet_object_to_Communication(tweet)
    tweet_info = comm.communicationMetadata.tweetInfo

    assert TWEET_ID_STR == comm.id
    assert TWEET_TXT == comm.text
    assert 1219842525 == comm.startTime
    assert 1219842525 == comm.endTime

    assert TWEET_ID == tweet_info.id
    assert 'jpn' == tweet_info.user.lang
    assert 'charman' == tweet_info.user.screenName
    assert 'C Harman' == tweet_info.user.name
    assert 1234 == tweet_info.user.id

    assert tweet_info.retweetedStatusId is None
    assert tweet_info.retweetedUserId is None
    assert tweet_info.retweetedScreenName is None

    assert REPLY_TWEET_ID == tweet_info.inReplyToStatusId
    assert 1236 == tweet_info.inReplyToUserId
    assert 'charman3' == tweet_info.inReplyToScreenName

    assert 1 == len(tweet_info.entities.hashtagList)
    assert u'lol' == tweet_info.entities.hashtagList[0].text
    assert 32 == tweet_info.entities.hashtagList[0].startOffset
    assert 36 == tweet_info.entities.hashtagList[0].endOffset

    assert u'Point' == tweet_info.coordinates.type
    assert -75.5 == tweet_info.coordinates.coordinates.longitude
    assert 40.25 == tweet_info.coordinates.coordinates.latitude

    assert u'Polygon' == tweet_info.place.boundingBox.type
    assert -77.25 == tweet_info.place.boundingBox.coordinateList[0].longitude
    assert 38.5 == tweet_info.place.boundingBox.coordinateList[0].latitude
    assert -76.0 == tweet_info.place.boundingBox.coordinateList[1].longitude
    assert 38.5 == tweet_info.place.boundingBox.coordinateList[1].latitude
    assert -76.0 == tweet_info.place.boundingBox.coordinateList[2].longitude
    assert 38.125 == tweet_info.place.boundingBox.coordinateList[2].latitude
    assert -77.25 == tweet_info.place.boundingBox.coordinateList[3].longitude
    assert 38.125 == tweet_info.place.boundingBox.coordinateList[3].latitude
    assert u'United States' == tweet_info.place.country
    assert u'US' == tweet_info.place.countryCode
    assert u'Washington, DC' == tweet_info.place.fullName
    assert u'01fbe706f872cb32' == tweet_info.place.id
    assert u'Washington' == tweet_info.place.name
    assert u'city' == tweet_info.place.placeType
    assert u'http://api.twitter.com/1/geo/id/01fbe706f872cb32.json' == \
        tweet_info.place.url

    assert 1 == len(comm.lidList)
    kvm = comm.lidList[0].languageToProbabilityMap
    assert 'eng' == kvm.keys()[0]
    assert 1.0 == kvm['eng']


def test_json_tweet_object_to_Communication_missing_in_reply_to(tweet):
    del tweet['in_reply_to_status_id']
    del tweet['in_reply_to_status_id_str']
    del tweet['in_reply_to_user_id']
    del tweet['in_reply_to_user_id_str']
    del tweet['in_reply_to_screen_name']

    comm = json_tweet_object_to_Communication(tweet)
    tweet_info = comm.communicationMetadata.tweetInfo

    assert TWEET_ID_STR == comm.id
    assert TWEET_TXT == comm.text
    assert 1219842525 == comm.startTime
    assert 1219842525 == comm.endTime

    assert TWEET_ID == tweet_info.id
    assert 'jpn' == tweet_info.user.lang
    assert 'charman' == tweet_info.user.screenName
    assert 'C Harman' == tweet_info.user.name
    assert 1234 == tweet_info.user.id

    assert RT_TWEET_ID == tweet_info.retweetedStatusId
    assert 1235 == tweet_info.retweetedUserId
    assert 'charman2' == tweet_info.retweetedScreenName

    assert tweet_info.inReplyToStatusId is None
    assert tweet_info.inReplyToUserId is None
    assert tweet_info.inReplyToScreenName is None

    assert 1 == len(tweet_info.entities.hashtagList)
    assert u'lol' == tweet_info.entities.hashtagList[0].text
    assert 32 == tweet_info.entities.hashtagList[0].startOffset
    assert 36 == tweet_info.entities.hashtagList[0].endOffset

    assert u'Point' == tweet_info.coordinates.type
    assert -75.5 == tweet_info.coordinates.coordinates.longitude
    assert 40.25 == tweet_info.coordinates.coordinates.latitude

    assert u'Polygon' == tweet_info.place.boundingBox.type
    assert -77.25 == tweet_info.place.boundingBox.coordinateList[0].longitude
    assert 38.5 == tweet_info.place.boundingBox.coordinateList[0].latitude
    assert -76.0 == tweet_info.place.boundingBox.coordinateList[1].longitude
    assert 38.5 == tweet_info.place.boundingBox.coordinateList[1].latitude
    assert -76.0 == tweet_info.place.boundingBox.coordinateList[2].longitude
    assert 38.125 == tweet_info.place.boundingBox.coordinateList[2].latitude
    assert -77.25 == tweet_info.place.boundingBox.coordinateList[3].longitude
    assert 38.125 == tweet_info.place.boundingBox.coordinateList[3].latitude
    assert u'United States' == tweet_info.place.country
    assert u'US' == tweet_info.place.countryCode
    assert u'Washington, DC' == tweet_info.place.fullName
    assert u'01fbe706f872cb32' == tweet_info.place.id
    assert u'Washington' == tweet_info.place.name
    assert u'city' == tweet_info.place.placeType
    assert u'http://api.twitter.com/1/geo/id/01fbe706f872cb32.json' == \
        tweet_info.place.url

    assert 1 == len(comm.lidList)
    kvm = comm.lidList[0].languageToProbabilityMap
    assert 'eng' == kvm.keys()[0]
    assert 1.0 == kvm['eng']
