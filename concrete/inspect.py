"""
"""

from collections import defaultdict
from operator import attrgetter


def print_conll_style_tags_for_communication(comm, char_offsets=False, dependency=False, lemmas=False, ner=False, pos=False):
    """Print 'ConLL-style' tags for the tokens in a Communication

    Args:
        comm: A Concrete Communication object
        char_offsets: A boolean flag for printing token text specified by
            a Token's (optional) TextSpan
        dependency: A boolean flag for printing dependency parse HEAD tags
        lemmas: A boolean flag for printing lemma tags
        ner: A boolean flag for printing Named Entity Recognition tags
        pos: A boolean flag for printing Part-of-Speech tags
    """
    header_fields = ["INDEX", "TOKEN"]
    if char_offsets:
        header_fields.append("CHAR")
    if lemmas:
        header_fields.append("LEMMA")
    if pos:
        header_fields.append("POS")
    if ner:
        header_fields.append("NER")
    if dependency:
        header_fields.append("HEAD")
    print "\t".join(header_fields)
    dashes = ["-"*len(fieldname) for fieldname in header_fields]
    print "\t".join(dashes)

    for tokenization in get_tokenizations(comm):
        token_tag_lists = []

        if char_offsets:
            token_tag_lists.append(get_char_offset_tags_for_tokenization(comm, tokenization))
        if lemmas:
            token_tag_lists.append(get_lemma_tags_for_tokenization(tokenization))
        if pos:
            token_tag_lists.append(get_pos_tags_for_tokenization(tokenization))
        if ner:
            token_tag_lists.append(get_ner_tags_for_tokenization(tokenization))
        if dependency:
            token_tag_lists.append(get_conll_head_tags_for_tokenization(tokenization))
        print_conll_style_tags_for_tokenization(tokenization, token_tag_lists)
        print


def print_conll_style_tags_for_tokenization(tokenization, token_tag_lists):
    """Print 'ConLL-style' tags for the tokens in a tokenization

    Args:
        tokenization: A Concrete Tokenization object
        token_tag_lists: A list of lists of token tag strings
    """
    if tokenization.tokenList:
        for i, token in enumerate(tokenization.tokenList.tokenList):
            token_tags = [str(token_tag_list[i]) for token_tag_list in token_tag_lists]
            fields = [str(i+1), token.text]
            fields.extend(token_tags)
            print "\t".join(fields)


def print_entities(comm):
    """Print information for all Entities and their EntityMentions

    Args:
        comm: A Concrete Communication
    """
    if comm.entitySetList:
        for entitySet_index, entitySet in enumerate(comm.entitySetList):
            if entitySet.metadata:
                print "Entity Set %d (%s):" % (entitySet_index, entitySet.metadata.tool)
            else:
                print "Entity Set %d:" % entitySet_index
            for entity_index, entity in enumerate(entitySet.entityList):
                print "  Entity %d-%d:" % (entitySet_index, entity_index)
                for entityMention_index, entityMention in enumerate(entity.mentionList):
                    print "      EntityMention %d-%d-%d:" % (entitySet_index, entity_index, entityMention_index)
                    print "          tokens:     %s" % " ".join(get_tokens_for_entityMention(entityMention))
                    if entityMention.text:
                        print "          text:       %s" % entityMention.text
                    print "          entityType: %s" % entityMention.entityType
                    print "          phraseType: %s" % entityMention.phraseType
                print
            print


def print_situation_mentions(comm):
    """Print information for all SituationMentions (which may not have Situations)

    Args:
        comm: A Concrete Communication
    """
    if comm.situationMentionSetList:
        for situationMentionSet_index, situationMentionSet in enumerate(comm.situationMentionSetList):
            if situationMentionSet.metadata:
                print "Situation Set %d (%s):" % (situationMentionSet_index, situationMentionSet.metadata.tool)
            else:
                print "Situation Set %d:" % situationMentionSet_index
            for situationMention_index, situationMention in enumerate(situationMentionSet.mentionList):
                print "  SituationMention %d-%d:" % (situationMentionSet_index, situationMention_index)
                _print_situation_mention(situationMention)
                print
            print


def print_situations(comm):
    """Print information for all Situations and their SituationMentions

    Args:
        comm: A Concrete Communication
    """

    if comm.situationSetList:
        for situationSet_index, situationSet in enumerate(comm.situationSetList):
            if situationSet.metadata:
                print "Situation Set %d (%s):" % (situationSet_index, situationSet.metadata.tool)
            else:
                print "Situation Set %d:" % situationSet_index
            for situation_index, situation in enumerate(situationSet.situationList):
                print "  Situation %d-%d:" % (situationSet_index, situation_index)
                _p(6, 18, "situationType", situation.situationType)
                if situation.mentionList:
                    for situationMention_index, situationMention in enumerate(situation.mentionList):
                        print " "*6 + "SituationMention %d-%d-%d:" % (
                            situationSet_index, situation_index, situationMention_index)
                        _print_situation_mention(situationMention)
                print
            print


def _print_situation_mention(situationMention):
    """Helper function for printing info for a SituationMention"""
    if situationMention.text:
        _p(10, 20, "text", situationMention.text)
    if situationMention.situationType:
        _p(10, 20, "situationType", situationMention.situationType)
    if situationMention.argumentList:
        for argument_index, mentionArgument in enumerate(situationMention.argumentList):
            print " "*10 + "Argument %d:" % argument_index
            if mentionArgument.role:
                _p(14, 16, "role", mentionArgument.role)
            if mentionArgument.entityMention:
                _p(14, 16, "entityMention",
                    " ".join(get_tokens_for_entityMention(mentionArgument.entityMention)))
            # A SituationMention can have an argumentList with a MentionArgument that
            # points to another SituationMention - which could conceivably lead to
            # loops.  We currently don't traverse the list recursively, instead looking
            # at only SituationMentions referenced by top-level SituationMentions
            if mentionArgument.situationMention:
                print " "*14 + "situationMention:"
                if situationMention.text:
                    _p(18, 20, "text", situationMention.text)
                if situationMention.situationType:
                    _p(18, 20, "situationType", situationMention.situationType)


def _p(indent_level, justified_width, fieldname, content):
    """Text alignment helper function"""
    print " "*indent_level + (fieldname + ":").ljust(justified_width) + content


def print_text_for_communication(comm):
    print comm.text


def print_tokens_with_entityMentions(comm):
    entityMentions_by_tokenizationId = get_entityMentions_by_tokenizationId(comm)
    entity_number_for_entityMention_uuid = get_entity_number_for_entityMention_uuid(comm)
    tokenizations_by_section = get_tokenizations_grouped_by_section(comm)

    for tokenizations_in_section in tokenizations_by_section:
        for tokenization in tokenizations_in_section:
            if tokenization.tokenList:
                text_tokens = [token.text for token in tokenization.tokenList.tokenList]
                if tokenization.uuid.uuidString in entityMentions_by_tokenizationId:
                    for entityMention in entityMentions_by_tokenizationId[tokenization.uuid.uuidString]:
                        # TODO: Handle non-contiguous tokens in a tokenIndexLists
                        first_token_index = entityMention.tokens.tokenIndexList[0]
                        last_token_index = entityMention.tokens.tokenIndexList[-1]
                        entity_number = entity_number_for_entityMention_uuid[entityMention.uuid.uuidString]
                        text_tokens[first_token_index] = "<ENTITY ID=%d>%s" % (entity_number, text_tokens[first_token_index])
                        text_tokens[last_token_index] = "%s</ENTITY>" % text_tokens[last_token_index]
                print " ".join(text_tokens)
        print


def print_tokens_for_communication(comm):
    """
    """
    tokenizations_by_section = get_tokenizations_grouped_by_section(comm)

    for tokenizations_in_section in tokenizations_by_section:
        for tokenization in tokenizations_in_section:
            if tokenization.tokenList:
                text_tokens = [token.text for token in tokenization.tokenList.tokenList]
                print " ".join(text_tokens)
        print


def print_penn_treebank_for_communication(comm):
    """Print Penn-Treebank parse trees for all tokenizations

    Args:
        comm: A Concrete Communication object
    """
    tokenizations = get_tokenizations(comm)

    for tokenization in tokenizations:
        if tokenization.parseList:
            for parse in tokenization.parseList:
                print penn_treebank_for_parse(parse) + "\n\n"


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
            for i, child_node_index in enumerate(nodes[node_index].childList):
                if i > 0:
                    s += "\n" + " "*indent
                s += _traverse_parse(nodes, child_node_index, indent)
            s += ")"
        else:
            s += nodes[node_index].tag
        return s

    sorted_nodes = sorted(parse.constituentList, key=attrgetter('id'))
    return _traverse_parse(sorted_nodes, 0)


def get_char_offset_tags_for_tokenization(comm, tokenization):
    """TODOC:
    """
    if tokenization.tokenList:
        char_offset_tags = [None]*len(tokenization.tokenList.tokenList)

        if comm.text:
            for i, token in enumerate(tokenization.tokenList.tokenList):
                if token.textSpan:
                    char_offset_tags[i] = comm.text[token.textSpan.start:token.textSpan.ending]
        return char_offset_tags


def get_conll_head_tags_for_tokenization(tokenization, dependency_parse_index=0):
    """Get a list of ConLL 'HEAD tags' for a tokenization

    In the ConLL data format:

        http://ufal.mff.cuni.cz/conll2009-st/task-description.html

    the HEAD for a token is the (1-indexed) index of that token's
    parent token.  The root token of the dependency parse has a HEAD
    index of 0.

    Args:
        tokenization: A Concrete Tokenization object

    Returns:
        A list of ConLL 'HEAD tag' strings, with one HEAD tag for each
        token in the supplied tokenization.  If a token does not have
        a HEAD tag (e.g. punctuation tokens), the HEAD tag is an empty
        string.

        If the tokenization does not have a Dependency Parse, this
        function returns a list of empty strings for each token in the
        supplied tokenization.
    """
    if tokenization.tokenList:
        # Tokens that are not part of the dependency parse
        # (e.g. punctuation) are represented using an empty string
        head_list = [""]*len(tokenization.tokenList.tokenList)

        if tokenization.dependencyParseList:
            for dependency in tokenization.dependencyParseList[dependency_parse_index].dependencyList:
                if dependency.gov is None:
                    head_list[dependency.dep] = 0
                else:
                    head_list[dependency.dep] = dependency.gov + 1
        return head_list
    else:
        return []


def get_entityMentions_by_tokenizationId(comm):
    """Get entity mentions for a Communication grouped by Tokenization UUID string

    Args:
        comm: A Concrete Communication object

    Returns:
        A dictionary of lists of EntityMentions, where the dictionary
        keys are Tokenization UUID strings.
    """
    mentions_by_tokenizationId = defaultdict(list)
    if comm.entitySetList:
        for entitySet in comm.entitySetList:
            for entity in entitySet.entityList:
                for entityMention in entity.mentionList:
                    mentions_by_tokenizationId[entityMention.tokens.tokenizationId.uuidString].append(entityMention)
    return mentions_by_tokenizationId


def get_entity_number_for_entityMention_uuid(comm):
    """Create mapping from EntityMention UUID to (zero-indexed) 'Entity Number'

    Args:
        comm: A Concrete Communication object

    Returns:
        A dictionary where the keys are EntityMention UUID strings,
        and the values are "Entity Numbers", where the first Entity is
        assigned number 0, the second Entity is assigned number 1,
        etc.
    """
    entity_number_for_entityMention_uuid = {}
    entity_number_counter = 0

    if comm.entitySetList:
        for entitySet in comm.entitySetList:
            for entity in entitySet.entityList:
                for entityMention in entity.mentionList:
                    entity_number_for_entityMention_uuid[entityMention.uuid.uuidString] = entity_number_counter
                entity_number_counter += 1
    return entity_number_for_entityMention_uuid


def get_lemma_tags_for_tokenization(tokenization, lemma_tokentagging_index=0):
    """Get lemma tags for a tokenization

    Args:
        tokenization: A Concrete Tokenization object

    Returns:
        A list of lemma tags for each token in the Tokenization
    """
    if tokenization.tokenList:
        lemma_tags = [""]*len(tokenization.tokenList.tokenList)
        lemma_tokentaggings = get_tokentaggings_of_type(tokenization, "lemma")
        if lemma_tokentaggings and len(lemma_tokentaggings) > lemma_tokentagging_index:
            tag_for_tokenIndex = {}
            for taggedToken in lemma_tokentaggings[lemma_tokentagging_index].taggedTokenList:
                tag_for_tokenIndex[taggedToken.tokenIndex] = taggedToken.tag
            for i, token in enumerate(tokenization.tokenList.tokenList):
                if i in tag_for_tokenIndex:
                    lemma_tags[i] = tag_for_tokenIndex[i]
        return lemma_tags


def get_ner_tags_for_tokenization(tokenization, ner_tokentagging_index=0):
    """Get Named Entity Recognition tags for a tokenization

    Args:
        tokenization: A Concrete Tokenization object

    Returns:
        A list of NER tags for each token in the Tokenization
    """
    if tokenization.tokenList:
        ner_tags = [""]*len(tokenization.tokenList.tokenList)
        ner_tokentaggings = get_tokentaggings_of_type(tokenization, "NER")
        if ner_tokentaggings and len(ner_tokentaggings) > ner_tokentagging_index:
            tag_for_tokenIndex = {}
            for taggedToken in ner_tokentaggings[ner_tokentagging_index].taggedTokenList:
                tag_for_tokenIndex[taggedToken.tokenIndex] = taggedToken.tag
            for i, token in enumerate(tokenization.tokenList.tokenList):
                try:
                    ner_tags[i] = tag_for_tokenIndex[i]
                except IndexError:
                    ner_tags[i] = ""
                if ner_tags[i] == "NONE":
                    ner_tags[i] = ""
        return ner_tags


def get_pos_tags_for_tokenization(tokenization, pos_tokentagging_index=0):
    """Get Part-of-Speech tags for a tokenization

    Args:
        tokenization: A Concrete Tokenization object

    Returns:
        A list of POS tags for each token in the Tokenization
    """
    if tokenization.tokenList:
        pos_tags = [""]*len(tokenization.tokenList.tokenList)
        pos_tokentaggings = get_tokentaggings_of_type(tokenization, "POS")
        if pos_tokentaggings and len(pos_tokentaggings) > pos_tokentagging_index:
            tag_for_tokenIndex = {}
            for taggedToken in pos_tokentaggings[pos_tokentagging_index].taggedTokenList:
                tag_for_tokenIndex[taggedToken.tokenIndex] = taggedToken.tag
            for i, token in enumerate(tokenization.tokenList.tokenList):
                if i in tag_for_tokenIndex:
                    pos_tags[i] = tag_for_tokenIndex[i]
        return pos_tags


def get_tokenizations(comm):
    """Returns a flat list of all Tokenization objects in a Communication

    Args:
        comm: A Concrete Communication

    Returns:
        A list of all Tokenization objects within the Communication
    """
    tokenizations = []

    if comm.sectionList:
        for section in comm.sectionList:
            if section.sentenceList:
                for sentence in section.sentenceList:
                    if sentence.tokenization:
                        tokenizations.append(sentence.tokenization)
    return tokenizations


def get_tokenizations_grouped_by_section(comm):
    """Returns a list of lists of Tokenization objects in a Communication

    Args:
        comm: A Concrete Communication

    Returns:
        Returns a list of lists of Tokenization objects, where the
        Tokenization objects are grouped by Section
    """
    tokenizations_by_section = []

    if comm.sectionList:
        for section in comm.sectionList:
            tokenizations_in_section = []
            if section.sentenceList:
                for sentence in section.sentenceList:
                    if sentence.tokenization:
                        tokenizations_in_section.append(sentence.tokenization)
            tokenizations_by_section.append(tokenizations_in_section)

    return tokenizations_by_section


def get_tokens_for_entityMention(entityMention):
    """Get list of token strings for an EntityMention

    Args:
        entityMention: A Concrete EntityMention argument

    Returns:
        A list of token strings
    """
    tokens = []
    for tokenIndex in entityMention.tokens.tokenIndexList:
        tokens.append(entityMention.tokens.tokenization.tokenList.tokenList[tokenIndex].text)
    return tokens


def get_tokentaggings_of_type(tokenization, taggingType):
    """Returns a list of TokenTagging objects with the specified taggingType

    Args:
        tokenization: A Concrete Tokenizaiton object
        taggingType: A string value for the specified TokenTagging.taggingType

    Returns:
        A list of TokenTagging objects
    """
    return [tt for tt in tokenization.tokenTaggingList if tt.taggingType.lower() == taggingType.lower()]
