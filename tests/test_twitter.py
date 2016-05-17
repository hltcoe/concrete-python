import unittest

from concrete.util.twitter import (json_tweet_object_to_Communication,
                                   twitter_lid_to_iso639_3)


class TestTwitter(unittest.TestCase):

    def test_twitter_lid_conversion(self):
        self.assertEquals('eng', twitter_lid_to_iso639_3('en-gb'))
        self.assertEquals('msa', twitter_lid_to_iso639_3('msa'))
        self.assertEquals('hun', twitter_lid_to_iso639_3('hu'))
        self.assertEquals('zho', twitter_lid_to_iso639_3('zh-cn'))
        self.assertEquals('zho', twitter_lid_to_iso639_3('zh-tw'))
        self.assertEquals('und', twitter_lid_to_iso639_3('und'))
        self.assertEquals('eng', twitter_lid_to_iso639_3('eng'))

    def test_json_tweet_string_to_TweetInfo(self):
        txt = ("Barber tells me - his son is colorblind / my hair is auburn /"
               " and auburn is a shade of green")
        id = u'238426131689242624'
        tweet_dict = {u"text": txt,
                      u"id_str": id,
                      u"user": {u"screen_name": "charman",
                                u'verified': False},
                      u'entities': {u"symbols": [],
                                    u'hashtags': [],
                                    u'user_mentions': [],
                                    u'urls': []},
                      u'coordinates': None,
                      u'place': None,
                      u"lang": u"en"}
        comm = json_tweet_object_to_Communication(tweet_dict)
        self.assertEquals(u'238426131689242624', comm.id)
        self.assertEquals(txt, comm.text)
        self.assertEquals(1, len(comm.lidList))
        self.assertEquals(u'238426131689242624', comm.id)
        kvm = comm.lidList[0].languageToProbabilityMap
        self.assertEquals("eng", kvm.keys()[0])
        self.assertEquals(1.0, kvm["eng"])
