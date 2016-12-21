"""Functions used by `concrete_inspect.py` to print data in a Communication.

The function implementations provide useful examples of how to
interact with many different Concrete datastructures.
"""

from concrete.util.metadata import get_index_of_tool
from concrete.util.unnone import lun
from collections import defaultdict
from operator import attrgetter


def _reconcile_index_and_tool(lst_of_conc, given_idx, tool):
    """Given a list of Concrete objects with metadata (e.g., `DependencyParse`s)
    and a default index, find the index of the object whose `.metadata.tool`
    matches the provided query tool name `tool`.

    When no tool is provided (but with an iterable list), this returns the
    provided default index (even if it\'s not a valid index).
    If the tool isn't found, the list is None or empty, this returns -1.
    """
    valid_lst = lst_of_conc is not None and len(lst_of_conc) > 0
    idx = given_idx if valid_lst else -1
    if tool is not None:
        idx = get_index_of_tool(lst_of_conc, tool)
    return idx


def _valid_index_lun(lst, idx):
    """Return True iff `idx` is a valid index into
    the given (non-None) list. If `lst` is None,
    return False.
    """

    if lst is None or len(lst) == 0:
        return False
    return idx >= 0 and idx < len(lst)


def print_conll_style_tags_for_communication(
        comm, char_offsets=False, dependency=False, lemmas=False, ner=False,
        pos=False,
        dependency_tool=None, lemmas_tool=None, ner_tool=None, pos_tool=None):

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
        header_fields.append(u"DEPREL")
    print u"\t".join(header_fields)
    dashes = ["-" * len(fieldname) for fieldname in header_fields]
    print u"\t".join(dashes)

    for tokenization in _get_tokenizations(comm):
        token_tag_lists = []

        if char_offsets:
            token_tag_lists.append(
                _get_char_offset_tags_for_tokenization(comm, tokenization))
        if lemmas:
            token_tag_lists.append(
                _get_lemma_tags_for_tokenization(tokenization,
                                                 tool=lemmas_tool))
        if pos:
            token_tag_lists.append(
                _get_pos_tags_for_tokenization(tokenization, tool=pos_tool))
        if ner:
            token_tag_lists.append(
                _get_ner_tags_for_tokenization(tokenization, tool=ner_tool))
        if dependency:
            token_tag_lists.append(
                _get_conll_head_tags_for_tokenization(tokenization,
                                                      tool=dependency_tool))
            token_tag_lists.append(
                _get_conll_deprel_tags_for_tokenization(tokenization,
                                                        tool=dependency_tool))
        print_conll_style_tags_for_tokenization(tokenization,
                                                token_tag_lists)
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


def print_entities(comm, tool=None):
    """Print information for all Entities and their EntityMentions

    Args:

    - `comm`: A Concrete Communication object
    """
    if comm.entitySetList:
        for entitySet_index, entitySet in enumerate(comm.entitySetList):
            if tool is None or entitySet.metadata.tool == tool:
                print u"Entity Set %d (%s):" % (entitySet_index,
                                                entitySet.metadata.tool)
                for entity_index, entity in enumerate(entitySet.entityList):
                    print u"  Entity %d-%d:" % (entitySet_index, entity_index)
                    for em_index, em in enumerate(entity.mentionList):
                        print u"      EntityMention %d-%d-%d:" % (
                            entitySet_index, entity_index, em_index)
                        print u"          tokens:     %s" % (
                            u" ".join(_get_tokens_for_entityMention(em)))
                        if em.text:
                            print u"          text:       %s" % em.text
                        print u"          entityType: %s" % em.entityType
                        print u"          phraseType: %s" % em.phraseType
                    print
                print


def print_metadata(comm, tool=None):
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

    if tool is None or comm.metadata.tool == tool:
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
    if tool is not None:
        dependency_parse_tools = dependency_parse_tools.intersection([tool])
        parse_tools = parse_tools.intersection([tool])
        tokenization_tools = tokenization_tools.intersection([tool])
        token_tagging_tools = token_tagging_tools.intersection([tool])

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
            if tool is None or em_set.metadata.tool == tool:
                print u"  EntityMentionSet #%d:  %s" % (
                    i, em_set.metadata.tool)
        print
    if comm.entitySetList:
        for i, entitySet in enumerate(comm.entitySetList):
            if tool is None or entitySet.metadata.tool == tool:
                print u"  EntitySet #%d:  %s" % (
                    i, entitySet.metadata.tool)
        print
    if comm.situationMentionSetList:
        for i, sm_set in enumerate(comm.situationMentionSetList):
            if tool is None or sm_set.metadata.tool == tool:
                print u"  SituationMentionSet #%d:  %s" % (
                    i, sm_set.metadata.tool)
        print
    if comm.situationSetList:
        for i, situationSet in enumerate(comm.situationSetList):
            if tool is None or situationSet.metadata.tool == tool:
                print u"  SituationSet #%d:  %s" % (
                    i, situationSet.metadata.tool)
        print


def print_sections(comm, tool=None):
    """Print information for all Sections, according to their spans.

    Args:

    - `comm`: A Concrete Communication
    """
    if tool is None or comm.metadata.tool == tool:
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


def print_situation_mentions(comm, tool=None):
    """Print information for all SituationMentions (some of which may
    not have Situations)

    Args:

    - `comm`: A Concrete Communication
    """
    for sm_set_idx, sm_set in enumerate(lun(comm.situationMentionSetList)):
        if tool is None or sm_set.metadata.tool == tool:
            print u"Situation Set %d (%s):" % (sm_set_idx,
                                               sm_set.metadata.tool)
            for sm_idx, sm in enumerate(sm_set.mentionList):
                print u"  SituationMention %d-%d:" % (sm_set_idx, sm_idx)
                _print_situation_mention(sm)
                print
            print


def print_situations(comm, tool=None):
    """Print information for all Situations and their SituationMentions

    Args:

    - `comm`: A Concrete Communication
    """
    for s_set_idx, s_set in enumerate(lun(comm.situationSetList)):
        if tool is None or s_set.metadata.tool == tool:
            print u"Situation Set %d (%s):" % (s_set_idx,
                                               s_set.metadata.tool)
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
                u" ".join(_get_tokens_for_entityMention(ma.entityMention)))
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


def print_text_for_communication(comm, tool=None):
    if tool is None or comm.metadata.tool == tool:
        print comm.text


def print_id_for_communication(comm, tool=None):
    if tool is None or comm.metadata.tool == tool:
        print comm.id


def print_tokens_with_entityMentions(comm, tool=None):
    em_by_tkzn_id = _get_entityMentions_by_tokenizationId(
        comm, tool=tool)
    em_entity_num = _get_entity_number_for_entityMention_uuid(comm, tool=tool)
    tokenizations_by_section = _get_tokenizations_grouped_by_section(comm)

    for tokenizations_in_section in tokenizations_by_section:
        for tokenization in tokenizations_in_section:
            if tokenization.tokenList:
                text_tokens = [token.text
                               for token
                               in tokenization.tokenList.tokenList]
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


def print_tokens_for_communication(comm, tool=None):
    """
    """
    tokenizations_by_section = _get_tokenizations_grouped_by_section(
        comm, tool=tool)

    for tokenizations_in_section in tokenizations_by_section:
        for tokenization in tokenizations_in_section:
            if tokenization.tokenList:
                text_tokens = [token.text
                               for token
                               in tokenization.tokenList.tokenList]
                print u" ".join(text_tokens)
        print


def print_penn_treebank_for_communication(comm, tool=None):
    """Print Penn-Treebank parse trees for all tokenizations

    Args:

    - `comm`: A Concrete Communication object
    """
    tokenizations = _get_tokenizations(comm)

    for tokenization in tokenizations:
        if tokenization.parseList:
            for parse in tokenization.parseList:
                if tool is None or tool == parse.metadata.tool:
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


def _get_char_offset_tags_for_tokenization(comm, tokenization):
    if tokenization.tokenList:
        char_offset_tags = [None] * len(tokenization.tokenList.tokenList)

        if comm.text:
            for i, token in enumerate(tokenization.tokenList.tokenList):
                if token.textSpan:
                    char_offset_tags[i] = comm.text[
                        token.textSpan.start:token.textSpan.ending]
        return char_offset_tags


def _deps_for_tokenization(tokenization,
                           dependency_parse_index=0,
                           tool=None):
    '''
    Return a generator of the dependencies (Dependency objects) for
    a tokenization under the given tool.
    '''
    if tokenization.tokenList is not None:
        # Tokens that are not part of the dependency parse
        # (e.g. punctuation) are represented using an empty string
        dp_idx = _reconcile_index_and_tool(tokenization.dependencyParseList,
                                           dependency_parse_index,
                                           tool)

        if _valid_index_lun(tokenization.dependencyParseList, dp_idx):
            dp = tokenization.dependencyParseList[dp_idx]
            if tool is None or dp.metadata.tool == tool:
                for dependency in dp.dependencyList:
                    yield dependency


def _sorted_dep_list_for_tokenization(tokenization,
                                      dependency_parse_index=0,
                                      tool=None):
    '''
    Return output of _deps_for_tokenization in a list whose length
    is equal to the number of tokens in this tokenization's token list,
    where the element at index i is a dependency if there is a
    dependency whose dep field is i and None otherwise.
    '''
    if tokenization.tokenList is not None:
        dep_list = [None] * len(tokenization.tokenList.tokenList)
        for dep in _deps_for_tokenization(
                tokenization, dependency_parse_index=dependency_parse_index,
                tool=tool):
            dep_list[dep.dep] = dep
        return dep_list
    else:
        return []


def _get_conll_head_tags_for_tokenization(tokenization,
                                          dependency_parse_index=0,
                                          tool=None):
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
    return map(
        lambda dep: '' if dep is None else (
            0 if dep.gov is None else dep.gov + 1),
        _sorted_dep_list_for_tokenization(
            tokenization, dependency_parse_index=dependency_parse_index,
            tool=tool))


def _get_conll_deprel_tags_for_tokenization(tokenization,
                                            dependency_parse_index=0,
                                            tool=None):
    """Get a list of ConLL 'DEPREL tags' for a tokenization

    In the ConLL data format:

        http://ufal.mff.cuni.cz/conll2009-st/task-description.html

    the DEPREL for a token is the type of that token's dependency with
    its parent.

    Args:

    - `tokenization`: A Concrete Tokenization object

    Returns:

    - A list of ConLL 'DEPREL tag' strings, with one DEPREL tag for each
      token in the supplied tokenization.  If a token does not have
      a DEPREL tag (e.g. punctuation tokens), the DEPREL tag is an empty
      string.

      If the tokenization does not have a Dependency Parse, this
      function returns a list of empty strings for each token in the
      supplied tokenization.
    """
    return map(
        lambda dep: '' if dep is None else (
            '' if dep.edgeType is None else dep.edgeType),
        _sorted_dep_list_for_tokenization(
            tokenization, dependency_parse_index=dependency_parse_index,
            tool=tool))


def _get_entityMentions_by_tokenizationId(comm, tool=None):
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
                if (tool is None or
                        entityMention.entityMentionSet.metadata.tool == tool):
                    u = entityMention.tokens.tokenizationId.uuidString
                    mentions_by_tkzn_id[u].append(entityMention)
    return mentions_by_tkzn_id


def _get_entity_number_for_entityMention_uuid(comm, tool=None):
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
                any_mention = False
                for entityMention in entity.mentionList:
                    if (tool is None or
                            entityMention.entityMentionSet.metadata.tool ==
                            tool):
                        entity_number_for_entityMention_uuid[
                            entityMention.uuid.uuidString
                        ] = entity_number_counter
                    any_mention = True
                if any_mention:
                    entity_number_counter += 1
    return entity_number_for_entityMention_uuid


def _get_lemma_tags_for_tokenization(tokenization, lemma_tokentagging_index=0,
                                     tool=None):
    """Get lemma tags for a tokenization

    Args:

    - `tokenization`: A Concrete Tokenization object

    Returns:

    - A list of lemma tags for each token in the Tokenization
    """
    if tokenization.tokenList:
        lemma_tags = [""] * len(tokenization.tokenList.tokenList)
        lemma_tts = _get_tokentaggings_of_type(tokenization, u"lemma",
                                               tool=tool)
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


def _get_ner_tags_for_tokenization(tokenization, ner_tokentagging_index=0,
                                   tool=None):
    """Get Named Entity Recognition tags for a tokenization

    Args:

    - `tokenization`: A Concrete Tokenization object

    Returns:

    - A list of NER tags for each token in the Tokenization
    """
    if tokenization.tokenList:
        ner_tags = [""] * len(tokenization.tokenList.tokenList)
        ner_tts = _get_tokentaggings_of_type(tokenization, u"NER", tool=tool)
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


def _get_pos_tags_for_tokenization(tokenization, pos_tokentagging_index=0,
                                   tool=None):
    """Get Part-of-Speech tags for a tokenization

    Args:

    - tokenization: A Concrete Tokenization object

    Returns:

    - A list of POS tags for each token in the Tokenization
    """
    if tokenization.tokenList:
        pos_tags = [""] * len(tokenization.tokenList.tokenList)
        pos_tts = _get_tokentaggings_of_type(tokenization, u"POS", tool=tool)
        if pos_tts and len(pos_tts) > pos_tokentagging_index:
            tag_for_tokenIndex = {}
            for taggedToken in pos_tts[pos_tokentagging_index].taggedTokenList:
                tag_for_tokenIndex[taggedToken.tokenIndex] = taggedToken.tag
            for i, token in enumerate(tokenization.tokenList.tokenList):
                if i in tag_for_tokenIndex:
                    pos_tags[i] = tag_for_tokenIndex[i]
        return pos_tags


def _get_tokenizations(comm, tool=None):
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
                        if (tool is None or
                                sentence.tokenization.metadata.tool == tool):
                            tokenizations.append(sentence.tokenization)
    return tokenizations


def _get_tokenizations_grouped_by_section(comm, tool=None):
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
                        if (tool is None or
                                sentence.tokenization.metadata.tool == tool):
                            tokenizations_in_section.append(
                                sentence.tokenization)
            tokenizations_by_section.append(tokenizations_in_section)

    return tokenizations_by_section


def _get_tokens_for_entityMention(entityMention):
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


def _get_tokentaggings_of_type(tokenization, taggingType, tool=None):
    """Returns a list of TokenTagging objects with the specified taggingType

    Args:

    - `tokenization`: A Concrete Tokenizaiton object
    - `taggingType`: A string value for the specified TokenTagging.taggingType

    Returns:

    - A list of TokenTagging objects
    """
    return [
        tt for tt in tokenization.tokenTaggingList
        if tt.taggingType.lower() == taggingType.lower() and (
            tool is None or tt.metadata.tool == tool)
    ]
