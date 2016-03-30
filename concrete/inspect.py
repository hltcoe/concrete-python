"""Functions used by `concrete_inspect.py` to print data in a Communication.

The function implementations provide useful examples of how to
interact with many different Concrete datastructures.
"""

from concrete.util.unnone import lun
from collections import defaultdict
from operator import attrgetter


def print_conll_style_tags_for_communication(
        comm, char_offsets=False, dependency=False, lemmas=False, ner=False,
        pos=False):

    """Print 'ConLL-style' tags for the tokens in a Communication

    Args:

    - `comm`: A Concrete Communication object
    - `char_offsets`: A boolean flag for printing token text specified by
          a Token's (optional) TextSpan
    - `dependency`: A boolean flag for printing dependency parse HEAD tags
    - `lemmas`: A boolean flag for printing lemma tags
    - `ner`: A boolean flag for printing Named Entity Recognition tags
    - `pos`: A boolean flag for printing Part-of-Speech tags
    """

    header_fields = [u"INDEX", u"TOKEN"]
    if char_offsets:
        header_fields.append(u"CHAR")
    if lemmas:
        header_fields.append(u"LEMMA")
    if pos:
        header_fields.append(u"POS")
    if ner:
        header_fields.append(u"NER")
    if dependency:
        header_fields.append(u"HEAD")
    print u"\t".join(header_fields)
    dashes = ["-" * len(fieldname) for fieldname in header_fields]
    print u"\t".join(dashes)

    for tokenization in get_tokenizations(comm):
        token_tag_lists = []

        if char_offsets:
            token_tag_lists.append(
                get_char_offset_tags_for_tokenization(comm, tokenization))
        if lemmas:
            token_tag_lists.append(
                get_lemma_tags_for_tokenization(tokenization))
        if pos:
            token_tag_lists.append(get_pos_tags_for_tokenization(tokenization))
        if ner:
            token_tag_lists.append(get_ner_tags_for_tokenization(tokenization))
        if dependency:
            token_tag_lists.append(
                get_conll_head_tags_for_tokenization(tokenization))
        print_conll_style_tags_for_tokenization(tokenization, token_tag_lists)
        print


def print_conll_style_tags_for_tokenization(tokenization, token_tag_lists):
    """Print 'ConLL-style' tags for the tokens in a tokenization

    Args:

    - `tokenization`: A Concrete Tokenization object
    - `token_tag_lists`: A list of lists of token tag strings
    """
    if tokenization.tokenList:
        for i, token in enumerate(tokenization.tokenList.tokenList):
            token_tags = [unicode(token_tag_list[i])
                          for token_tag_list in token_tag_lists]
            fields = [unicode(i + 1), token.text]
            fields.extend(token_tags)
            print u"\t".join(fields)


def print_entities(comm):
    """Print information for all Entities and their EntityMentions

    Args:

    - `comm`: A Concrete Communication object
    """
    if comm.entitySetList:
        for entitySet_index, entitySet in enumerate(comm.entitySetList):
            if entitySet.metadata:
                print u"Entity Set %d (%s):" % (entitySet_index,
                                                entitySet.metadata.tool)
            else:
                print u"Entity Set %d:" % entitySet_index
            for entity_index, entity in enumerate(entitySet.entityList):
                print u"  Entity %d-%d:" % (entitySet_index, entity_index)
                for em_index, em in enumerate(entity.mentionList):
                    print u"      EntityMention %d-%d-%d:" % (
                        entitySet_index, entity_index, em_index)
                    print u"          tokens:     %s" % (
                        u" ".join(get_tokens_for_entityMention(em)))
                    if em.text:
                        print u"          text:       %s" % em.text
                    print u"          entityType: %s" % em.entityType
                    print u"          phraseType: %s" % em.phraseType
                print
            print


def print_metadata(comm):
    """Print metadata for tools used to annotate Communication
    """
    def _get_tokenizations(comm):
        tokenizations = []
        if comm.sectionList:
            for section in comm.sectionList:
                if section.sentenceList:
                    for sentence in section.sentenceList:
                        if sentence.tokenization:
                            tokenizations.append(sentence.tokenization)
        return tokenizations

    print u"Communication:  %s\n" % comm.metadata.tool

    dependency_parse_tools = set()
    parse_tools = set()
    tokenization_tools = set()
    token_tagging_tools = set()
    for tokenization in _get_tokenizations(comm):
        tokenization_tools.add(tokenization.metadata.tool)
        if tokenization.tokenTaggingList:
            for tokenTagging in tokenization.tokenTaggingList:
                token_tagging_tools.add(tokenTagging.metadata.tool)
        if tokenization.dependencyParseList:
            for dependencyParse in tokenization.dependencyParseList:
                dependency_parse_tools.add(dependencyParse.metadata.tool)
        if tokenization.parseList:
            for parse in tokenization.parseList:
                parse_tools.add(parse.metadata.tool)

    if tokenization_tools:
        for toolname in sorted(tokenization_tools):
            print u"  Tokenization:  %s" % toolname
        print
    if dependency_parse_tools:
        for toolname in sorted(dependency_parse_tools):
            print u"    Dependency Parse:  %s" % toolname
        print
    if parse_tools:
        for toolname in sorted(parse_tools):
            print u"    Parse:  %s" % toolname
        print
    if token_tagging_tools:
        for toolname in sorted(token_tagging_tools):
            print u"    TokenTagging:  %s" % toolname
        print

    if comm.entityMentionSetList:
        for i, em_set in enumerate(comm.entityMentionSetList):
            print u"  EntityMentionSet #%d:  %s" % (i, em_set.metadata.tool)
        print
    if comm.entitySetList:
        for i, entitySet in enumerate(comm.entitySetList):
            print u"  EntitySet #%d:  %s" % (i, entitySet.metadata.tool)
        print
    if comm.situationMentionSetList:
        for i, sm_set in enumerate(comm.situationMentionSetList):
            print u"  SituationMentionSet #%d:  %s" % (i, sm_set.metadata.tool)
        print
    if comm.situationSetList:
        for i, situationSet in enumerate(comm.situationSetList):
            print u"  SituationSet #%d:  %s" % (i, situationSet.metadata.tool)
        print


def print_sections(comm):
    """Print information for all Sections, according to their spans.

    Args:

    - `comm`: A Concrete Communication
    """
    text = comm.text
    for sect_idx, sect in enumerate(lun(comm.sectionList)):
        ts = sect.textSpan
        if ts is None:
            print u"Section %s does not have a textSpan "
            "field set" % (sect.uuid.uuidString)
            continue
        print u"Section %d (%s), from %d to %d:" % (
            sect_idx, sect.uuid.uuidString, ts.start, ts.ending)
        print u"%s" % (text[ts.start:ts.ending])
        print
    print


def print_situation_mentions(comm):
    """Print information for all SituationMentions (some of which may
    not have Situations)

    Args:

    - `comm`: A Concrete Communication
    """
    for sm_set_idx, sm_set in enumerate(lun(comm.situationMentionSetList)):
        if sm_set.metadata:
            print u"Situation Set %d (%s):" % (sm_set_idx,
                                               sm_set.metadata.tool)
        else:
            print u"Situation Set %d:" % sm_set_idx
        for sm_idx, sm in enumerate(sm_set.mentionList):
            print u"  SituationMention %d-%d:" % (sm_set_idx, sm_idx)
            _print_situation_mention(sm)
            print
        print


def print_situations(comm):
    """Print information for all Situations and their SituationMentions

    Args:

    - `comm`: A Concrete Communication
    """
    for s_set_idx, s_set in enumerate(lun(comm.situationSetList)):
        if s_set.metadata:
            print u"Situation Set %d (%s):" % (s_set_idx, s_set.metadata.tool)
        else:
            print u"Situation Set %d:" % s_set_idx
        for s_idx, situation in enumerate(s_set.situationList):
            print u"  Situation %d-%d:" % (s_set_idx, s_idx)
            _p(6, 18, u"situationType", situation.situationType)
            for sm_idx, sm in enumerate(lun(situation.mentionList)):
                print u" " * 6 + u"SituationMention %d-%d-%d:" % (
                    s_set_idx, s_idx, sm_idx)
                _print_situation_mention(sm)
            print
        print


def _print_situation_mention(situationMention):
    """Helper function for printing info for a SituationMention"""
    if situationMention.text:
        _p(10, 20, u"text", situationMention.text)
    if situationMention.situationType:
        _p(10, 20, u"situationType", situationMention.situationType)
    for arg_idx, ma in enumerate(lun(situationMention.argumentList)):
        print u" " * 10 + u"Argument %d:" % arg_idx
        if ma.role:
            _p(14, 16, u"role", ma.role)
        if ma.entityMention:
            _p(14, 16, u"entityMention",
                u" ".join(get_tokens_for_entityMention(ma.entityMention)))
        # A SituationMention can have an argumentList with a
        # MentionArgument that points to another SituationMention---
        # which could conceivably lead to loops.  We currently don't
        # traverse the list recursively, instead looking at only
        # SituationMentions referenced by top-level SituationMentions
        if ma.situationMention:
            print u" " * 14 + u"situationMention:"
            if situationMention.text:
                _p(18, 20, u"text", situationMention.text)
            if situationMention.situationType:
                _p(18, 20, u"situationType", situationMention.situationType)


def _p(indent_level, justified_width, fieldname, content):
    """Text alignment helper function"""
    print (
        (u" " * indent_level) +
        (fieldname + u":").ljust(justified_width) +
        content
    )


def print_text_for_communication(comm):
    print comm.text


def print_tokens_with_entityMentions(comm):
    em_by_tkzn_id = get_entityMentions_by_tokenizationId(
        comm)
    em_entity_num = get_entity_number_for_entityMention_uuid(comm)
    tokenizations_by_section = get_tokenizations_grouped_by_section(comm)

    for tokenizations_in_section in tokenizations_by_section:
        for tokenization in tokenizations_in_section:
            if tokenization.tokenList:
                text_tokens = [
                    token.text for token in tokenization.tokenList.tokenList]
                u = tokenization.uuid.uuidString
                if u in em_by_tkzn_id:
                    for em in em_by_tkzn_id[u]:
                        first_token_index = em.tokens.tokenIndexList[0]
                        last_token_index = em.tokens.tokenIndexList[-1]
                        entity_number = em_entity_num[em.uuid.uuidString]
                        text_tokens[first_token_index] = (
                            u"<ENTITY ID=%d>%s" %
                            (entity_number, text_tokens[first_token_index])
                        )
                        text_tokens[last_token_index] = (
                            u"%s</ENTITY>" % text_tokens[last_token_index]
                        )
                print u" ".join(text_tokens)
        print


def print_tokens_for_communication(comm):
    """
    """
    tokenizations_by_section = get_tokenizations_grouped_by_section(comm)

    for tokenizations_in_section in tokenizations_by_section:
        for tokenization in tokenizations_in_section:
            if tokenization.tokenList:
                text_tokens = [
                    token.text for token in tokenization.tokenList.tokenList]
                print u" ".join(text_tokens)
        print


def print_penn_treebank_for_communication(comm):
    """Print Penn-Treebank parse trees for all tokenizations

    Args:

    - `comm`: A Concrete Communication object
    """
    tokenizations = get_tokenizations(comm)

    for tokenization in tokenizations:
        if tokenization.parseList:
            for parse in tokenization.parseList:
                print penn_treebank_for_parse(parse) + u"\n\n"


def penn_treebank_for_parse(parse):
    """Get a Penn-Treebank style string for a Concrete Parse object

    Args:

    - `parse`: A Concrete Parse object

    Returns:

    - A string containing a Penn Treebank style parse tree representation
    """
    def _traverse_parse(nodes, node_index, indent=0):
        s = u""
        indent += len(nodes[node_index].tag) + 2
        if nodes[node_index].childList:
            s += u"(%s " % nodes[node_index].tag
            for i, child_node_index in enumerate(nodes[node_index].childList):
                if i > 0:
                    s += u"\n" + u" " * indent
                s += _traverse_parse(nodes, child_node_index, indent)
            s += u")"
        else:
            s += nodes[node_index].tag
        return s

    sorted_nodes = sorted(parse.constituentList, key=attrgetter('id'))
    return _traverse_parse(sorted_nodes, 0)


def get_char_offset_tags_for_tokenization(comm, tokenization):
    if tokenization.tokenList:
        char_offset_tags = [None] * len(tokenization.tokenList.tokenList)

        if comm.text:
            for i, token in enumerate(tokenization.tokenList.tokenList):
                if token.textSpan:
                    char_offset_tags[i] = comm.text[
                        token.textSpan.start:token.textSpan.ending]
        return char_offset_tags


def get_conll_head_tags_for_tokenization(tokenization,
                                         dependency_parse_index=0):
    """Get a list of ConLL 'HEAD tags' for a tokenization

    In the ConLL data format:

        http://ufal.mff.cuni.cz/conll2009-st/task-description.html

    the HEAD for a token is the (1-indexed) index of that token's
    parent token.  The root token of the dependency parse has a HEAD
    index of 0.

    Args:

    - `tokenization`: A Concrete Tokenization object

    Returns:

    - A list of ConLL 'HEAD tag' strings, with one HEAD tag for each
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
        head_list = [""] * len(tokenization.tokenList.tokenList)

        if tokenization.dependencyParseList:
            dpl = tokenization.dependencyParseList[dependency_parse_index]
            for dependency in dpl.dependencyList:
                if dependency.gov is None:
                    head_list[dependency.dep] = 0
                else:
                    head_list[dependency.dep] = dependency.gov + 1
        return head_list
    else:
        return []


def get_entityMentions_by_tokenizationId(comm):
    """Get entity mentions for a Communication grouped by Tokenization
    UUID string

    Args:

    - `comm`: A Concrete Communication object

    Returns:

    - A dictionary of lists of EntityMentions, where the dictionary
      keys are Tokenization UUID strings.
    """
    mentions_by_tkzn_id = defaultdict(list)
    for entitySet in lun(comm.entitySetList):
        for entity in entitySet.entityList:
            for entityMention in entity.mentionList:
                u = entityMention.tokens.tokenizationId.uuidString
                mentions_by_tkzn_id[u].append(entityMention)
    return mentions_by_tkzn_id


def get_entity_number_for_entityMention_uuid(comm):
    """Create mapping from EntityMention UUID to (zero-indexed)
    'Entity Number'

    Args:

    - `comm`: A Concrete Communication object

    Returns:

    - A dictionary where the keys are EntityMention UUID strings,
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
                    entity_number_for_entityMention_uuid[
                        entityMention.uuid.uuidString] = entity_number_counter
                entity_number_counter += 1
    return entity_number_for_entityMention_uuid


def get_lemma_tags_for_tokenization(tokenization, lemma_tokentagging_index=0):
    """Get lemma tags for a tokenization

    Args:

    - `tokenization`: A Concrete Tokenization object

    Returns:

    - A list of lemma tags for each token in the Tokenization
    """
    if tokenization.tokenList:
        lemma_tags = [""] * len(tokenization.tokenList.tokenList)
        lemma_tts = get_tokentaggings_of_type(tokenization, u"lemma")
        if (lemma_tts and
                len(lemma_tts) > lemma_tokentagging_index):
            tag_for_tokenIndex = {}
            tt = lemma_tts[lemma_tokentagging_index]
            for taggedToken in tt.taggedTokenList:
                tag_for_tokenIndex[taggedToken.tokenIndex] = taggedToken.tag
            for i, token in enumerate(tokenization.tokenList.tokenList):
                if i in tag_for_tokenIndex:
                    lemma_tags[i] = tag_for_tokenIndex[i]
        return lemma_tags


def get_ner_tags_for_tokenization(tokenization, ner_tokentagging_index=0):
    """Get Named Entity Recognition tags for a tokenization

    Args:

    - `tokenization`: A Concrete Tokenization object

    Returns:

    - A list of NER tags for each token in the Tokenization
    """
    if tokenization.tokenList:
        ner_tags = [""] * len(tokenization.tokenList.tokenList)
        ner_tts = get_tokentaggings_of_type(tokenization, u"NER")
        if (ner_tts and
                len(ner_tts) > ner_tokentagging_index):
            tag_for_tokenIndex = {}
            for taggedToken in ner_tts[ner_tokentagging_index].taggedTokenList:
                tag_for_tokenIndex[taggedToken.tokenIndex] = taggedToken.tag
            for i, token in enumerate(tokenization.tokenList.tokenList):
                try:
                    ner_tags[i] = tag_for_tokenIndex[i]
                except IndexError:
                    ner_tags[i] = u""
                if ner_tags[i] == u"NONE":
                    ner_tags[i] = u""
        return ner_tags


def get_pos_tags_for_tokenization(tokenization, pos_tokentagging_index=0):
    """Get Part-of-Speech tags for a tokenization

    Args:

    - tokenization: A Concrete Tokenization object

    Returns:

    - A list of POS tags for each token in the Tokenization
    """
    if tokenization.tokenList:
        pos_tags = [""] * len(tokenization.tokenList.tokenList)
        pos_tts = get_tokentaggings_of_type(tokenization, u"POS")
        if pos_tts and len(pos_tts) > pos_tokentagging_index:
            tag_for_tokenIndex = {}
            for taggedToken in pos_tts[pos_tokentagging_index].taggedTokenList:
                tag_for_tokenIndex[taggedToken.tokenIndex] = taggedToken.tag
            for i, token in enumerate(tokenization.tokenList.tokenList):
                if i in tag_for_tokenIndex:
                    pos_tags[i] = tag_for_tokenIndex[i]
        return pos_tags


def get_tokenizations(comm):
    """Returns a flat list of all Tokenization objects in a Communication

    Args:

    - `comm`: A Concrete Communication

    Returns:

    - A list of all Tokenization objects within the Communication
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

    - `comm`: A Concrete Communication

    Returns:

    - Returns a list of lists of Tokenization objects, where the
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

    - `entityMention`: A Concrete EntityMention argument

    Returns:

    - A list of token strings
    """
    tokens = []
    for tokenIndex in entityMention.tokens.tokenIndexList:
        tokens.append(entityMention.tokens.tokenization.tokenList.tokenList[
                      tokenIndex].text)
    return tokens


def get_tokentaggings_of_type(tokenization, taggingType):
    """Returns a list of TokenTagging objects with the specified taggingType

    Args:

    - `tokenization`: A Concrete Tokenizaiton object
    - `taggingType`: A string value for the specified TokenTagging.taggingType

    Returns:

    - A list of TokenTagging objects
    """
    return [
        tt for tt in tokenization.tokenTaggingList
        if tt.taggingType.lower() == taggingType.lower()
    ]
