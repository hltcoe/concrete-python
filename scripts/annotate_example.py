#!/usr/bin/env python

"""
"""

import argparse
import json
import time

import concrete
import concrete.util
from concrete.validate import validate_communication


def main():
    comm = create_comm_from_tweet(JSON_TWEET_STRING)
    concrete.util.write_communication_to_file(comm, "tweet.comm")
    add_dictionary_tagging(comm)
    concrete.util.write_communication_to_file(comm, "tweet_pos.comm")


def create_comm_from_tweet(json_tweet_string):
    """Create a Concrete Communication from a JSON Tweet string

    Args:
        json_tweet_string: A JSON string for a Tweet, using the JSON
            format specified by the Twitter API:
              https://dev.twitter.com/docs/platform-objects/tweets

    Returns:
        A Concrete Communication object
    """
    tweet_data = json.loads(json_tweet_string)

    comm = concrete.Communication()
    comm.id = "Annotation_Test_1"
    comm.metadata = concrete.AnnotationMetadata(
        tool="Annotation Example script",
        timestamp=int(time.time())
    )
    comm.text = tweet_data['text']
    comm.type = "Tweet"
    comm.uuid = concrete.util.generate_UUID()

    comm.sectionList = [concrete.Section()]
    comm.sectionList[0].kind = "mySectionKind"
    comm.sectionList[0].uuid = concrete.util.generate_UUID()
    comm.sectionList[0].sentenceList = [concrete.Sentence()]
    comm.sectionList[0].sentenceList[0].uuid = concrete.util.generate_UUID()
    comm.sectionList[0].sentenceList[0].tokenization = concrete.Tokenization()

    tokenization = comm.sectionList[0].sentenceList[0].tokenization
    tokenization.kind = concrete.TokenizationKind.TOKEN_LIST
    tokenization.metadata = concrete.AnnotationMetadata(tool="TEST", timestamp=int(time.time()))
    tokenization.tokenList = concrete.TokenList()
    tokenization.tokenList.tokenList = []
    tokenization.uuid = concrete.util.generate_UUID()

    # Whitespace tokenization
    tokens = comm.text.split()

    for i, token_text in enumerate(tokens):
        t = concrete.Token()
        t.tokenIndex = i
        t.text = token_text
        tokenization.tokenList.tokenList.append(t)

    if validate_communication(comm):
        print "Created valid Communication"
    else:
        print "ERROR: Invalid Communication"

    return comm


def add_dictionary_tagging(comm):
    """Adds In/Out of dictionary 'POS' tags to a Communication

    Takes a Concrete Communication, adds a Part-Of-Speech tag to each
    token, where the tags record whether the token is 'In' or 'Out' of
    the system dictionary.

    Args:
        comm: A Concrete Communication with tokens

    Returns:
        A copy of the original Communication, with POS tags added
    """
    dictionary = set()
    for w in open('/usr/share/dict/words'):
        dictionary.add(w.strip().lower())

    if comm.sectionList:
        for section in comm.sectionList:
            if section.sentenceList:
                for sentence in section.sentenceList:
                    posTagList = concrete.TokenTagging()
                    posTagList.metadata = concrete.AnnotationMetadata(tool="POS Tagger", timestamp=int(time.time()))
                    posTagList.taggingType = "POS"
                    posTagList.taggedTokenList = []
                    posTagList.uuid = concrete.util.generate_UUID()
                    if sentence.tokenization.tokenList:
                        for i, token in enumerate(sentence.tokenization.tokenList.tokenList):
                            tt = concrete.TaggedToken()
                            tt.tokenIndex = i
                            if token.text.lower() in dictionary:
                                tt.tag = "In"
                            else:
                                tt.tag = "Out"
                            posTagList.taggedTokenList.append(tt)
                            print "%d [%s] %s" % (i, token.text, tt.tag)
                    sentence.tokenization.tokenTaggingList = [posTagList]
            print

    if validate_communication(comm):
        print "Created valid POS tagging for Communication"
    else:
        print "ERROR: Invalid POS tagging Communication"
    return comm


def write_communication_to_file(communication, communication_filename):
    return write_thrift_to_file(communication, communication_filename)

def write_thrift_to_file(thrift_obj, filename):
    thrift_bytes = TSerialization.serialize(thrift_obj)
    thrift_file = open(filename, "w")
    thrift_file.write(thrift_bytes)
    thrift_file.close()


JSON_TWEET_STRING = '{"contributors": null, "truncated": false, "text": "Barber tells me - his son is colorblind / my hair is auburn / and auburn is a shade of green", "in_reply_to_status_id": null, "id": 238426131689242624, "favorite_count": 0, "source": "<a href=\\"http://twitter.com\\" rel=\\"nofollow\\">Twitter Web Client</a>", "retweeted": false, "coordinates": null, "entities": {"symbols": [], "user_mentions": [], "hashtags": [], "urls": []}, "in_reply_to_screen_name": null, "id_str": "238426131689242624", "retweet_count": 0, "in_reply_to_user_id": null, "favorited": false, "user": {"follow_request_sent": null, "profile_use_background_image": true, "default_profile_image": false, "id": 18063351, "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme5/bg.gif", "verified": false, "profile_text_color": "3E4415", "profile_image_url_https": "https://pbs.twimg.com/profile_images/67158916/n3703917_32092098_7623_normal.jpg", "profile_sidebar_fill_color": "99CC33", "entities": {"url": {"urls": [{"url": "http://t.co/Qb6hKcbqgj", "indices": [0, 22], "expanded_url": "http://craigharman.net", "display_url": "craigharman.net"}]}, "description": {"urls": []}}, "followers_count": 78, "profile_sidebar_border_color": "829D5E", "id_str": "18063351", "profile_background_color": "352726", "listed_count": 5, "is_translation_enabled": false, "utc_offset": -14400, "statuses_count": 26, "description": "", "friends_count": 54, "location": "", "profile_link_color": "D02B55", "profile_image_url": "http://pbs.twimg.com/profile_images/67158916/n3703917_32092098_7623_normal.jpg", "following": null, "geo_enabled": false, "profile_background_image_url": "http://abs.twimg.com/images/themes/theme5/bg.gif", "screen_name": "charman", "lang": "en", "profile_background_tile": false, "favourites_count": 0, "name": "Craig Harman", "notifications": null, "url": "http://t.co/Qb6hKcbqgj", "created_at": "Thu Dec 11 23:07:27 +0000 2008", "contributors_enabled": false, "time_zone": "Eastern Time (US & Canada)", "protected": false, "default_profile": false, "is_translator": false}, "geo": null, "in_reply_to_user_id_str": null, "lang": "en", "created_at": "Thu Aug 23 00:03:14 +0000 2012", "in_reply_to_status_id_str": null, "place": null}\n'


if __name__ == "__main__":
    main()
