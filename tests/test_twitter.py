from pytest import fixture

from concrete.util.twitter import (json_tweet_object_to_Communication,
                                   twitter_lid_to_iso639_3)


TWEET_TXT = ("Barber tells me - his son is colorblind / my hair is auburn /"
             " and auburn is a shade of green")

TWEET_ID = u'238426131689242624'


@fixture
def tweet():
    return {u"text": TWEET_TXT,
            u"id_str": TWEET_ID,
            u'created_at': 'Wed Aug 27 13:08:45 +0000 2008',
            u"user": {u"screen_name": "charman",
                      u"lang": "ja",
                      u'verified': False},
            u'entities': {u"symbols": [],
                          u'hashtags': [],
                          u'user_mentions': [],
                          u'urls': []},
            u'coordinates': None,
            u'place': None,
            u"lang": u"en"}


def test_twitter_lid_conversion():
    assert 'eng' == twitter_lid_to_iso639_3('en-gb')
    assert 'msa' == twitter_lid_to_iso639_3('msa')
    assert 'hun' == twitter_lid_to_iso639_3('hu')
    assert 'zho' == twitter_lid_to_iso639_3('zh-cn')
    assert 'zho' == twitter_lid_to_iso639_3('zh-tw')
    assert 'und' == twitter_lid_to_iso639_3('und')
    assert 'eng' == twitter_lid_to_iso639_3('eng')


def test_json_tweet_object_to_Communication_with_lang(tweet):
    comm = json_tweet_object_to_Communication(tweet)
    assert TWEET_ID == comm.id
    assert TWEET_TXT == comm.text
    assert 1 == len(comm.lidList)
    assert 1219842525 == comm.startTime
    assert 1219842525 == comm.endTime
    assert "jpn" == comm.communicationMetadata.tweetInfo.user.lang
    kvm = comm.lidList[0].languageToProbabilityMap
    assert "eng" == kvm.keys()[0]
    assert 1.0 == kvm["eng"]


def test_json_tweet_object_to_Communication_without_lang(tweet):
    del tweet['lang']
    comm = json_tweet_object_to_Communication(tweet)
    assert comm.lidList is None
