import unittest
import json

from concrete.util.twitter import json_tweet_object_to_Communication


class TestTwitter(unittest.TestCase):

    def test_json_tweet_string_to_TweetInfo(self):
        json_tweet_string = u'{"contributors": null, "truncated": false, "text\
": "Barber tells me - his son is colorblind / my hair is auburn / and auburn i\
s a shade of green", "in_reply_to_status_id": null, "id": 238426131689242624, \
"favorite_count": 0, "source": "<a href=\\"http://twitter.com\\" rel=\\"nofoll\
ow\\">Twitter Web Client</a>", "retweeted": false, "coordinates": null, "entit\
ies": {"symbols": [], "user_mentions": [], "hashtags": [], "urls": []}, "in_re\
ply_to_screen_name": null, "id_str": "238426131689242624", "retweet_count": 0,\
 "in_reply_to_user_id": null, "favorited": false, "user": {"follow_request_sen\
t": null, "profile_use_background_image": true, "default_profile_image": false\
, "id": 18063351, "profile_background_image_url_https": "https://abs.twimg.com\
/images/themes/theme5/bg.gif", "verified": false, "profile_text_color": "3E441\
5", "profile_image_url_https": "https://pbs.twimg.com/profile_images/67158916/\
n3703917_32092098_7623_normal.jpg", "profile_sidebar_fill_color": "99CC33", "e\
ntities": {"url": {"urls": [{"url": "http://t.co/Qb6hKcbqgj", "indices": [0, 2\
2], "expanded_url": "http://craigharman.net", "display_url": "craigharman.net"\
}]}, "description": {"urls": []}}, "followers_count": 78, "profile_sidebar_bor\
der_color": "829D5E", "id_str": "18063351", "profile_background_color": "35272\
6", "listed_count": 5, "is_translation_enabled": false, "utc_offset": -14400, \
"statuses_count": 26, "description": "", "friends_count": 54, "location": "", \
"profile_link_color": "D02B55", "profile_image_url": "http://pbs.twimg.com/pro\
file_images/67158916/n3703917_32092098_7623_normal.jpg", "following": null, "g\
eo_enabled": false, "profile_background_image_url": "http://abs.twimg.com/imag\
es/themes/theme5/bg.gif", "screen_name": "charman", "lang": "en", "profile_bac\
kground_tile": false, "favourites_count": 0, "name": "Craig Harman", "notifica\
tions": null, "url": "http://t.co/Qb6hKcbqgj", "created_at": "Thu Dec 11 23:07\
:27 +0000 2008", "contributors_enabled": false, "time_zone": "Eastern Time (US\
 & Canada)", "protected": false, "default_profile": false, "is_translator": fa\
lse}, "geo": null, "in_reply_to_user_id_str": null, "lang": "en", "created_at"\
: "Thu Aug 23 00:03:14 +0000 2012", "in_reply_to_status_id_str": null, "place"\
: null}\n'
        jso = json.loads(json_tweet_string)
        comm = json_tweet_object_to_Communication(jso)

        self.assertEquals(1, len(comm.lidList))
        kvm = comm.lidList[0].languageToProbabilityMap
        self.assertEquals("en", kvm.keys()[0])
        self.assertEquals(1.0, kvm["en"])
