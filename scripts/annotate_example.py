#!/usr/bin/env python

"""
"""

import argparse
import json

import concrete
import concrete.util
from concrete.validate import validate_communication

DICTIONARY = set()


def main():
    comm = create_comm_from_tweet(JSON_TWEET_STRING)
    concrete.util.write_communication_to_file(comm, "tweet.comm")

    for w in open('/usr/share/dict/words'):
        DICTIONARY.add(w.strip())

    add_dictionary_tagging(comm)

    concrete.util.write_communication_to_file(comm, "tweet_pos.comm")


def create_comm_from_tweet(json_tweet_string):
    """
    """
    tweet_data = json.loads(json_tweet_string)

    comm = concrete.Communication()
    comm.id = "Annotation_Test_1"
    comm.text = tweet_data['text']
    comm.type = "Tweet"
    comm.uuid = concrete.util.generate_UUID()

    comm.sectionSegmentations = [concrete.SectionSegmentation()]
    comm.sectionSegmentations[0].uuid = concrete.util.generate_UUID()
    comm.sectionSegmentations[0].sectionList = [concrete.Section()]
    comm.sectionSegmentations[0].sectionList[0].kind = "mySectionKind"
    comm.sectionSegmentations[0].sectionList[0].uuid = concrete.util.generate_UUID()
    comm.sectionSegmentations[0].sectionList[0].sentenceSegmentation = [concrete.SentenceSegmentation()]
    comm.sectionSegmentations[0].sectionList[0].sentenceSegmentation[0].sectionId = comm.sectionSegmentations[0].sectionList[0].uuid
    comm.sectionSegmentations[0].sectionList[0].sentenceSegmentation[0].uuid = concrete.util.generate_UUID()
    comm.sectionSegmentations[0].sectionList[0].sentenceSegmentation[0].sentenceList = [concrete.Sentence()]
    comm.sectionSegmentations[0].sectionList[0].sentenceSegmentation[0].sentenceList[0].uuid = concrete.util.generate_UUID()
    comm.sectionSegmentations[0].sectionList[0].sentenceSegmentation[0].sentenceList[0].tokenizationList = [concrete.Tokenization()]

    tokenization = comm.sectionSegmentations[0].sectionList[0].sentenceSegmentation[0].sentenceList[0].tokenizationList[0]
    tokenization.kind = concrete.TokenizationKind.TOKEN_LIST
    tokenization.uuid = concrete.util.generate_UUID()
    tokenization.tokenList = concrete.TokenList()
    tokenization.tokenList.tokens = []

    # Whitespace tokenization
    tokens = comm.text.split()

    for i, token_text in enumerate(tokens):
        t = concrete.Token()
        t.tokenIndex = i
        t.text = token_text
        tokenization.tokenList.tokens.append(t)

    if validate_communication(comm):
        print "Created valid Communication"
    else:
        print "ERROR: Invalid Communication"

    return comm


def add_dictionary_tagging(comm):
    """
    """
    if comm.sectionSegmentations:
        for sectionSegmentation in comm.sectionSegmentations:
            for section in sectionSegmentation.sectionList:
                if section.sentenceSegmentation:
                    for sentenceSegmentation in section.sentenceSegmentation:
                        for sentence in sentenceSegmentation.sentenceList:
                            for tokenization in sentence.tokenizationList:
                                tokenization.posTagList = concrete.TokenTagging()
                                tokenization.posTagList.uuid = concrete.util.generate_UUID()
                                tokenization.posTagList.taggedTokenList = []
                                if tokenization.tokenList:
                                    for i, token in enumerate(tokenization.tokenList.tokens):
                                        tt = concrete.TaggedToken()
                                        tt.tokenIndex = i
                                        if token.text in DICTIONARY:
                                            tt.tag = "In"
                                        else:
                                            tt.tag = "Out"
                                        tokenization.posTagList.taggedTokenList.append(tt)
                                        print "%d [%s] %s" % (i, token.text, tt.tag)
                            print

    if validate_communication(comm):
        print "Created valid POS tagging for Communication"
    else:
        print "ERROR: Invalid POS tagging Communication"
    return comm


JSON_TWEET_STRING = '{"created_at":"Thu May 02 18:43:59 +0000 2013","id":330029921764253696,"id_str":"330029921764253696","text":"Love the feel of my shears sliding thru hair makes me feel alive hope u luv it cut my beautiful one @iHATEmrtampa #addicted2hair","source":"\\u003ca href=\\"http:\\/\\/twitter.com\\/download\\/iphone\\" rel=\\"nofollow\\"\\u003eTwitter for iPhone\\u003c\\/a\\u003e","truncated":false,"in_reply_to_status_id":null,"in_reply_to_status_id_str":null,"in_reply_to_user_id":null,"in_reply_to_user_id_str":null,"in_reply_to_screen_name":null,"user":{"id":915753656,"id_str":"915753656","name":"Jacque Roker Asberry","screen_name":"lovehairJacque","location":"San Antonio ","url":null,"description":"Love doing hair raising my kids and my fun job @AE live to love -love to live oh yea love being a BMS mommy","protected":false,"followers_count":22,"friends_count":75,"listed_count":0,"created_at":"Tue Oct 30 23:51:26 +0000 2012","favourites_count":86,"utc_offset":-18000,"time_zone":"Eastern Time (US & Canada)","geo_enabled":false,"verified":false,"statuses_count":128,"lang":"en","contributors_enabled":false,"is_translator":false,"profile_background_color":"642D8B","profile_background_image_url":"http:\\/\\/a0.twimg.com\\/images\\/themes\\/theme10\\/bg.gif","profile_background_image_url_https":"https:\\/\\/si0.twimg.com\\/images\\/themes\\/theme10\\/bg.gif","profile_background_tile":true,"profile_image_url":"http:\\/\\/a0.twimg.com\\/profile_images\\/2786831753\\/a2b215368cd60c347a6c039e8be54cee_normal.jpeg","profile_image_url_https":"https:\\/\\/si0.twimg.com\\/profile_images\\/2786831753\\/a2b215368cd60c347a6c039e8be54cee_normal.jpeg","profile_banner_url":"https:\\/\\/si0.twimg.com\\/profile_banners\\/915753656\\/1365821121","profile_link_color":"FF0000","profile_sidebar_border_color":"65B0DA","profile_sidebar_fill_color":"7AC3EE","profile_text_color":"3D1957","profile_use_background_image":true,"default_profile":false,"default_profile_image":false,"following":null,"follow_request_sent":null,"notifications":null},"geo":null,"coordinates":null,"place":null,"contributors":null,"retweet_count":0,"favorite_count":0,"entities":{"hashtags":[{"text":"addicted2hair","indices":[114,128]}],"symbols":[],"urls":[],"user_mentions":[{"screen_name":"iHATEmrtampa","name":"Sherri Allgood","id":1283503873,"id_str":"1283503873","indices":[100,113]}]},"favorited":false,"retweeted":false,"filter_level":"medium","lang":"en"}'


if __name__ == "__main__":
    main()
