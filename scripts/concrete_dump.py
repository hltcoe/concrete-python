#!/usr/bin/env python

"""Command-line utility to print human-readable information about a
Communication to stdout
"""

import argparse
from collections import defaultdict

import concrete.util


def main():
    parser = argparse.ArgumentParser(description="Print information about a Concrete Communication to stdout")
    parser.add_argument("--mentions", help="",
                        action="store_true")
    parser.add_argument("--pos", help="Print Part-Of-Speech tags in 'pseudo-ConLL' format",
                        action="store_true")
    parser.add_argument("--tokens", help="Print whitespace-seperated tokens for *all* Tokenizations in a "
                        "Communication.  There is one line per sentence, and section breaks are marked by '-'",
                        action="store_true")
    parser.add_argument("--treebank", help="Print Penn-Treebank style parse trees for *all* Constituent "
                        "Parses in the Communication",
                        action="store_true")
    parser.add_argument("communication_file")
    args = parser.parse_args()

    comm = concrete.util.read_communication_from_file(args.communication_file)

    if args.mentions:
        print_tokens_with_entity_mentions(comm)
    if args.pos:
        print_pos_tags_for_communication(comm)
    if args.tokens:
        print_tokens_for_communication(comm)
    if args.treebank:
        print_penn_treebank_for_communication(comm)


def print_pos_tags_for_communication(comm):
    """
    """
    tokenizations = get_tokenizations(comm)

    for tokenization in tokenizations:
        if tokenization.tokenList and tokenization.posTagList:
            tag_for_tokenIndex = {}
            for tagged_token in tokenization.posTagList.taggedTokenList:
                tag_for_tokenIndex[tagged_token.tokenIndex] = tagged_token.tag
            for i, token in enumerate(tokenization.tokenList.tokens):
                try:
                    pos_tag = tag_for_tokenIndex[i]
                except IndexError:
                    pos_tag = ""
                print "%d\t%s\t%s" % (i+1, token.text, pos_tag)
            print


def print_tokens_with_entity_mentions(comm):
    entity_mentions_by_tokenization_id = get_entity_mentions_by_tokenization_id(comm)
    entity_number_for_entity_mention_id = get_entity_numbers_for_entity_mention_ids(comm)
    tokenizations_by_section = get_tokenizations_by_section(comm)

    for tokenizations_in_section in tokenizations_by_section:
        for tokenization in tokenizations_in_section:
            if tokenization.tokenList:
                text_tokens = [token.text for token in tokenization.tokenList.tokens]
                if tokenization.uuid.uuidString in entity_mentions_by_tokenization_id:
                    for entity_mention in entity_mentions_by_tokenization_id[tokenization.uuid.uuidString]:
                        first_token_index = entity_mention.tokens.tokenIndexList[0]
                        last_token_index = entity_mention.tokens.tokenIndexList[-1]
                        entity_number = entity_number_for_entity_mention_id[entity_mention.uuid.uuidString]
                        text_tokens[first_token_index] = "<ENTITY ID=%d>%s" % (entity_number, text_tokens[first_token_index])
                        text_tokens[last_token_index] = "%s</ENTITY>" % text_tokens[last_token_index]
                print " ".join(text_tokens)
        print "-"


def print_tokens_for_communication(comm):
    """
    """
    tokenizations_by_section = get_tokenizations_by_section(comm)

    for tokenizations_in_section in tokenizations_by_section:
        for tokenization in tokenizations_in_section:
            if tokenization.tokenList:
                text_tokens = [token.text for token in tokenization.tokenList.tokens]
                print " ".join(text_tokens)
        print "-"


def print_penn_treebank_for_communication(comm):
    """Print Penn-Treebank parse trees for all tokenizations

    Args:
        comm: A Concrete Communication object
    """
    tokenizations = get_tokenizations(comm)

    for tokenization in tokenizations:
        if tokenization.parse:
            print penn_treebank_for_parse(tokenization.parse) + "\n\n"


def penn_treebank_for_parse(parse):
    """Get a Penn-Treebank style string for a Concrete Parse object

    Args:
        parse: A Concrete Parse object

    Returns:
        A string containing a Penn Treebank style parse tree representation
    """
    def _traverse_parse(nodes, node_index, indent=0):
        s = ""
        indent += len(nodes[node_index].tag) + 2
        if nodes[node_index].childList:
            s += "(%s " % nodes[node_index].tag
            for i, node_index in enumerate(nodes[node_index].childList):
                if i > 0:
                    s += "\n" + " "*indent
                s += _traverse_parse(nodes, node_index, indent)
            s += ")"
        else:
            s += nodes[node_index].tag
        return s

    return _traverse_parse(parse.constituentList, 0)


def get_entity_mentions_by_tokenization_id(comm):
    """Get entity mentions for a Communication grouped by Tokenization UUID string

    Args:
        comm: A Concrete Communication object

    Returns:
        A dictionary lists of EntityMentions, where the dictionary
        keys are Tokenization UUID strings.
    """
    mentions_by_tokenization_id = defaultdict(list)
    if comm.entitySets:
        for entitySet in comm.entitySets:
            for entity in entitySet.entityList:
                for entityMention in entity.mentionList:
                    mentions_by_tokenization_id[entityMention.tokens.tokenizationId.uuidString].append(entityMention)
    return mentions_by_tokenization_id


def get_entity_numbers_for_entity_mention_ids(comm):
    """Create mapping from EntityMention UUID to (zero-indexed) "Entity Number"

    Args:
        comm: A Concrete Communication object

    Returns:
        A dictionary where the keys are EntityMention UUID strings,
        and the values are "Entity Numbers", where the first Entity is
        assigned number 0, the second Entity is assigned number 1,
        etc.

    """
    entity_numbers_for_entity_mention_ids = {}
    entity_number_counter = 0

    if comm.entitySets:
        for entitySet in comm.entitySets:
            for entity in entitySet.entityList:
                for entityMention in entity.mentionList:
                    entity_numbers_for_entity_mention_ids[entityMention.uuid.uuidString] = entity_number_counter
                entity_number_counter += 1
    return entity_numbers_for_entity_mention_ids


def get_tokenizations(comm):
    """Returns a flat list of all Tokenization objects in a Communication

    Args:
        comm: A Concrete Communication

    Returns:
        A list of all Tokenization objects within the Communication
    """
    tokenizations = []

    if comm.sectionSegmentations:
        for sectionSegmentation in comm.sectionSegmentations:
            for section in sectionSegmentation.sectionList:
                if section.sentenceSegmentation:
                    for sentenceSegmentation in section.sentenceSegmentation:
                        for sentence in sentenceSegmentation.sentenceList:
                            for tokenization in sentence.tokenizationList:
                                tokenizations.append(tokenization)
    return tokenizations


def get_tokenizations_by_section(comm):
    """Returns a list of lists of Tokenization objects in a Communication

    Args:
        comm: A Concrete Communication

    Returns:
        Returns a list of lists of Tokenization objects, where the
        Tokenization objects are grouped by Section
    """
    tokenizations_by_section = []

    if comm.sectionSegmentations:
        for sectionSegmentation in comm.sectionSegmentations:
            for section in sectionSegmentation.sectionList:
                tokenizations_in_section = []
                if section.sentenceSegmentation:
                    for sentenceSegmentation in section.sentenceSegmentation:
                        for sentence in sentenceSegmentation.sentenceList:
                            for tokenization in sentence.tokenizationList:
                                tokenizations_in_section.append(tokenization)
                tokenizations_by_section.append(tokenizations_in_section)

    return tokenizations_by_section


if __name__ == "__main__":
    main()
