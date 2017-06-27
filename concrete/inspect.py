"""Functions used by `concrete_inspect.py` to print data in a Communication.

The function implementations provide useful examples of how to
interact with many different Concrete datastructures.
"""
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import defaultdict
from operator import attrgetter

from .util.metadata import filter_unnone, tool_to_filter
from .util.unnone import lun
from .util.tokenization import get_tokenizations, get_token_taggings

try:
    unicode
except NameError:
    unicode = str


def _get_tagged_token_strs_by_token_index(tagged_tokens, num_tokens):
    '''
    Return list of `num_tokens` strings:
    the specified token tag at each token index if a tag exists at that
    index, else the empty string.

    Args:
        tagged_tokens (list): list of :class:`.TaggedToken` objects
        num_tokens (int): number of tokens

    Returns:
        list of token tags (or empty strings for untagged tokens)
    '''
    tagged_tokens_by_token_index = dict(
        (tagged_token.tokenIndex, tagged_token)
        for tagged_token in tagged_tokens
    )
    return [
        (
            tagged_tokens_by_token_index[token_index].tag
            if token_index in tagged_tokens_by_token_index
            else u''
        )
        for token_index in range(num_tokens)
    ]


def print_conll_style_tags_for_communication(
        comm, char_offsets=False, dependency=False, lemmas=False, ner=False,
        pos=False,
        dependency_tool=None, dependency_parse_filter=None,
        lemmas_tool=None, lemmas_filter=None,
        ner_tool=None, ner_filter=None,
        pos_tool=None, pos_filter=None,
        other_tags=None):

    """
    Print 'CoNLL-style' tags for the tokens in a Communication.
    If column is requested (for example, `ner` is set to `True`) but
    there is no such annotation in the communication, that column is
    not printed (the header is not printed either).  If there is more
    than one such annotation in the communication, one column is printed
    for each annotation.  In the event of differing numbers of
    annotations per Tokenization, all annotations are printed, but it is
    not guaranteed that the columns of two different tokenizations
    correspond to one another.

    Args:
        comm (Communication):
        char_offsets (bool): Flag for printing token text specified by
          a :class:`.Token`'s (optional) :class:`.TextSpan`
        dependency (bool): Flag for printing dependency parse HEAD tags
        dependency_tool (str): Deprecated.
            If not `None`, only print information for
            :class:`.DependencyParse` objects if they have a matching
            `metadata.tool` field
        dependency_parse_filter (func): If not None, print information
            for only those :class:`.DependencyParse` objects that pass
            this filter.  Should be a function that takes a list of
            annotations (objects with metadata fields) and returns a
            list of annotations (possibly filtered and re-ordered).
        lemmas (bool): Flag for printing lemma tags
            (:class:`.TokenTagging` objects of type LEMMA)
        lemmas_tool (str): Deprecated.
            If not `None`, only print information for
            :class:`.TokenTagging` objects of type LEMMA if they have
            a matching `metadata.tool` field
        lemmas_filter (func): If not None, print information
            for only those LEMMA taggings that pass
            this filter.  Should be a function that takes a list of
            annotations (objects with metadata fields) and returns a
            list of annotations (possibly filtered and re-ordered).
        ner (bool): Flag for printing Named Entity Recognition tags
            (:class:`.TokenTagging` objects of type NER)
        ner_tool (str): Deprecated.
            If not `None`, only print information for
            :class:`.TokenTagging` objects of type NER if they have
            a matching `metadata.tool` field
        ner_filter (func): If not None, print information
            for only those NER taggings that pass
            this filter.  Should be a function that takes a list of
            annotations (objects with metadata fields) and returns a
            list of annotations (possibly filtered and re-ordered).
        pos (bool): Flag for printing Part-of-Speech tags
            (:class:`.TokenTagging` objects of type POS)
        pos_tool (str): Deprecated.
            If not `None`, only print information for
            :class:`.TokenTagging` objects of type POS if they have
            a matching `metadata.tool` field
        pos_filter (func): If not None, print information
            for only those POS taggings that pass
            this filter.  Should be a function that takes a list of
            annotations (objects with metadata fields) and returns a
            list of annotations (possibly filtered and re-ordered).
        other_tags (dict): Map of other tagging types to print (as keys)
            to annotation filters, or None.  If the value (annotation
            filter) of a given tagging type is not None, print
            information for only those taggings that pass
            the filter (should be a function that takes a list of
            annotations (objects with metadata fields) and returns a
            list of annotations (possibly filtered and re-ordered)).
    """
    dependency_parse_filter = filter_unnone(tool_to_filter(
        dependency_tool, dependency_parse_filter))
    lemmas_filter = filter_unnone(tool_to_filter(
        lemmas_tool, lemmas_filter))
    ner_filter = filter_unnone(tool_to_filter(
        ner_tool, ner_filter))
    pos_filter = filter_unnone(tool_to_filter(
        pos_tool, pos_filter))

    if other_tags is None:
        other_tags = dict()

    header_fields_by_tokenization = []
    field_lists_by_tokenization = []

    for tokenization in get_tokenizations(comm):
        header_fields = []
        field_lists = []

        header_fields.append(u'INDEX')
        field_lists.append([
            unicode(i + 1)
            for i in range(len(tokenization.tokenList.tokenList))
        ])

        header_fields.append(u'TOKEN')
        field_lists.append([
            token.text
            for token in tokenization.tokenList.tokenList
        ])

        if char_offsets:
            header_fields.append(u'CHAR')
            field_lists.append(
                _get_char_offset_tags_for_tokenization(comm, tokenization))

        if lemmas:
            for token_tagging in lemmas_filter(
                    get_token_taggings(tokenization, u'LEMMA')):
                header_fields.append(u'LEMMA')
                field_lists.append(
                    _get_tagged_token_strs_by_token_index(
                        token_tagging.taggedTokenList,
                        len(tokenization.tokenList.tokenList)))

        if pos:
            for token_tagging in pos_filter(
                    get_token_taggings(tokenization, u'POS')):
                header_fields.append(u'POS')
                field_lists.append(
                    _get_tagged_token_strs_by_token_index(
                        token_tagging.taggedTokenList,
                        len(tokenization.tokenList.tokenList)))

        if ner:
            for token_tagging in ner_filter(
                    get_token_taggings(tokenization, u'NER')):
                header_fields.append(u'NER')
                field_lists.append([
                    (tag if tag != u'NONE' else u'')
                    for tag in _get_tagged_token_strs_by_token_index(
                        token_tagging.taggedTokenList,
                        len(tokenization.tokenList.tokenList)
                    )
                ])

        if dependency:
            for conll_tag_pair_list in _get_conll_tags_for_tokenization(
                    tokenization,
                    dependency_parse_filter=dependency_parse_filter):
                header_fields.append(u'HEAD')
                field_lists.append([p[0] for p in conll_tag_pair_list])
                header_fields.append(u'DEPREL')
                field_lists.append([p[1] for p in conll_tag_pair_list])

        for (tag, tag_filter) in other_tags.items():
            _filter = filter_unnone(tag_filter)
            for token_tagging in _filter(get_token_taggings(tokenization, tag)):
                header_fields.append(tag)
                field_lists.append(
                    _get_tagged_token_strs_by_token_index(
                        token_tagging.taggedTokenList,
                        len(tokenization.tokenList.tokenList)))

        header_fields_by_tokenization.append(header_fields)
        field_lists_by_tokenization.append(field_lists)

    if len(set(map(tuple, header_fields_by_tokenization))) > 1:
        logging.warning(
            'communication does not have same taggings for each tokenization')

    def _max_num_header_fields(header_field):
        return max(
            header_fields.count(header_field)
            for header_fields
            in header_fields_by_tokenization
        )

    overall_header_fields = (
        ([u'INDEX'] * _max_num_header_fields(u'INDEX')) +
        ([u'TOKEN'] * _max_num_header_fields(u'TOKEN')) +
        ([u'CHAR'] * _max_num_header_fields(u'CHAR')) +
        ([u'LEMMA'] * _max_num_header_fields(u'LEMMA')) +
        ([u'POS'] * _max_num_header_fields(u'POS')) +
        ([u'NER'] * _max_num_header_fields(u'NER')) +
        ([u'HEAD', u'DEPREL'] * _max_num_header_fields(u'HEAD'))
    )
    for tag in other_tags:
        overall_header_fields.extend([tag] * _max_num_header_fields(tag))

    print(u'\t'.join(overall_header_fields))
    print(u'\t'.join(u'-' * len(header) for header in overall_header_fields))

    for (header_fields, field_lists) in zip(
            header_fields_by_tokenization, field_lists_by_tokenization):
        for row in zip(*field_lists):
            def _generate_row():
                overall_field_num = 0
                for (field_num, header) in enumerate(header_fields):
                    while header != overall_header_fields[overall_field_num]:
                        yield u''
                        overall_field_num += 1
                    yield row[field_num]
                    overall_field_num += 1
            print('\t'.join(_generate_row()))
        print()


def _print_entity_mention_content(em, prefix=''):
    '''
    Print information for :class:`.EntityMention` `em`, prefixing each
    line by `prefix`.

    Args:
        em (EntityMention):
        prefix (str):
    '''
    print(prefix + u"tokens:     %s" % (
        u" ".join(_get_tokens_for_entityMention(em))))
    if em.text:
        print(prefix + u"text:       %s" % em.text)
    print(prefix + u"entityType: %s" % em.entityType)
    print(prefix + u"phraseType: %s" % em.phraseType)


def print_entities(comm, tool=None, entity_set_filter=None):
    """Print information for :class:`.Entity` objects and their
    associated :class:`.EntityMention` objects

    Args:
        comm (Communication):
        tool (str): Deprecated.
                    If not `None`, only print information for
                    :class:`.EntitySet` objects with a matching
                    `metadata.tool` field
        entity_set_filter (func): If not None, print information
            for only those :class:`.EntitySet` objects that pass
            this filter.  Should be a function that takes a list of
            annotations (objects with metadata fields) and returns a
            list of annotations (possibly filtered and re-ordered).
    """
    _filter = filter_unnone(tool_to_filter(tool, entity_set_filter))
    for (entitySet_index, entitySet) in enumerate(lun(comm.entitySetList)):
        if _filter([entitySet]):
            print(u"Entity Set %d (%s):" % (entitySet_index,
                                            entitySet.metadata.tool))
            for entity_index, entity in enumerate(entitySet.entityList):
                print(u"  Entity %d-%d:" % (entitySet_index, entity_index))
                for em_index, em in enumerate(entity.mentionList):
                    print(u"      EntityMention %d-%d-%d:" % (
                        entitySet_index, entity_index, em_index))
                    _print_entity_mention_content(em, prefix=' ' * 10)
                    for (cm_index, cm) in enumerate(em.childMentionList):
                        print(u"          child EntityMention #%d:" % cm_index)
                        _print_entity_mention_content(cm, prefix=' ' * 14)
                print()
            print()


def print_metadata(comm, tool=None, annotation_filter=None):
    """Print metadata tools used to annotate Communication

    Args:
        comm (Communication):
        tool (str): Deprecated.
                    If not `None`, only print :class:`.AnnotationMetadata`
                    information for objects with a matching
                    `metadata.tool` field
        annotation_filter (func): If not None, print information
            for only those objects that pass this filter.  Should be a
            function that takes a list of annotations (objects with
            metadata fields) and returns a list of annotations (possibly
            filtered and re-ordered).
    """
    _filter = filter_unnone(tool_to_filter(tool, annotation_filter))
    if _filter([comm]):
        print(u"Communication:  %s\n" % comm.metadata.tool)

    dependency_parse_tools = set()
    parse_tools = set()
    tokenization_tools = set()
    token_tagging_tools = set()

    tokenizations = get_tokenizations(comm)
    tokenization_tools.update(
        ann.metadata.tool
        for ann in _filter(tokenizations))
    for tokenization in tokenizations:
        token_tagging_tools.update(
            ann.metadata.tool
            for ann in _filter(lun(tokenization.tokenTaggingList)))
        dependency_parse_tools.update(
            ann.metadata.tool
            for ann in _filter(lun(tokenization.dependencyParseList)))
        parse_tools.update(
            ann.metadata.tool
            for ann in _filter(lun(tokenization.parseList)))

    communication_tagging_tools = set(
        ann.metadata.tool
        for ann in _filter(lun(comm.communicationTaggingList)))

    if tokenization_tools:
        for toolname in sorted(tokenization_tools):
            print(u"  Tokenization:  %s" % toolname)
        print()
    if dependency_parse_tools:
        for toolname in sorted(dependency_parse_tools):
            print(u"    Dependency Parse:  %s" % toolname)
        print()
    if parse_tools:
        for toolname in sorted(parse_tools):
            print(u"    Parse:  %s" % toolname)
        print()
    if token_tagging_tools:
        for toolname in sorted(token_tagging_tools):
            print(u"    TokenTagging:  %s" % toolname)
        print()

    if comm.entityMentionSetList:
        for i, em_set in enumerate(comm.entityMentionSetList):
            if _filter([em_set]):
                print(u"  EntityMentionSet #%d:  %s" % (
                    i, em_set.metadata.tool))
        print()
    if comm.entitySetList:
        for i, entitySet in enumerate(comm.entitySetList):
            if _filter([entitySet]):
                print(u"  EntitySet #%d:  %s" % (
                    i, entitySet.metadata.tool))
        print()
    if comm.situationMentionSetList:
        for i, sm_set in enumerate(comm.situationMentionSetList):
            if _filter([sm_set]):
                print(u"  SituationMentionSet #%d:  %s" % (
                    i, sm_set.metadata.tool))
        print()
    if comm.situationSetList:
        for i, situationSet in enumerate(comm.situationSetList):
            if _filter([situationSet]):
                print(u"  SituationSet #%d:  %s" % (
                    i, situationSet.metadata.tool))
        print()

    if communication_tagging_tools:
        for toolname in sorted(communication_tagging_tools):
            print(u"  CommunicationTagging:  %s" % toolname)
        print()


def print_sections(comm, tool=None, communication_filter=None):
    """
    Print information for all :class:`.Section` object, according to
    their spans.

    Args:
        comm (Communication):
        tool (str): Deprecated.
                    If not `None`, only print information for
                    :class:`.Section` objects with a matching
                    `metadata.tool` field
        communication_filter (func): If not None, print information
            for only those :class:`.Communication` objects that pass
            this filter.  Should be a function that takes a list of
            annotations (objects with metadata fields) and returns a
            list of annotations (possibly filtered and re-ordered).
    """
    _filter = filter_unnone(tool_to_filter(tool, communication_filter))
    if _filter([comm]):
        text = comm.text
        for sect_idx, sect in enumerate(lun(comm.sectionList)):
            ts = sect.textSpan
            if ts is None:
                print(u"Section %s does not have a textSpan ")
                "field set" % (sect.uuid.uuidString)
                continue
            print(u"Section %d (%s), from %d to %d:" % (
                sect_idx, sect.uuid.uuidString, ts.start, ts.ending))
            print(u"%s" % (text[ts.start:ts.ending]))
            print()
        print()


def print_situation_mentions(comm, tool=None, situation_mention_set_filter=None):
    """
    Print information for all :class:`.SituationMention`s (some of which
    may not have a :class:`.Situation`)

    Args:
        comm (Communication):
        tool (str): Deprecated.
                    If not `None`, only print information for
                    :class:`.SituationMention` objects with a matching
                    `metadata.tool` field
        situation_mention_set_filter (func): If not None, print information
            for only those :class:`.SituationMentionSet` objects that pass
            this filter.  Should be a function that takes a list of
            annotations (objects with metadata fields) and returns a
            list of annotations (possibly filtered and re-ordered).
    """
    _filter = filter_unnone(tool_to_filter(tool, situation_mention_set_filter))
    for sm_set_idx, sm_set in enumerate(lun(comm.situationMentionSetList)):
        if _filter([sm_set]):
            print(u"Situation Set %d (%s):" % (sm_set_idx,
                                               sm_set.metadata.tool))
            for sm_idx, sm in enumerate(sm_set.mentionList):
                print(u"  SituationMention %d-%d:" % (sm_set_idx, sm_idx))
                _print_situation_mention(sm)
                print()
            print()


def print_situations(comm, tool=None, situation_set_filter=None):
    """
    Print information for all :class:`.Situation` objects and their
    associated :class:`.SituationMention` objects

    Args:
        comm (Communication):
        tool (str): Deprecated.
                    If not `None`, only print information for
                    :class:`.Situation` objects with a matching
                    `metadata.tool` field
        situation_set_filter (func): If not None, print information
            for only those :class:`.SituationSet` objects that pass
            this filter.  Should be a function that takes a list of
            annotations (objects with metadata fields) and returns a
            list of annotations (possibly filtered and re-ordered).
    """
    _filter = filter_unnone(tool_to_filter(tool, situation_set_filter))
    for s_set_idx, s_set in enumerate(lun(comm.situationSetList)):
        if _filter([s_set]):
            print(u"Situation Set %d (%s):" % (s_set_idx,
                                               s_set.metadata.tool))
            for s_idx, situation in enumerate(s_set.situationList):
                print(u"  Situation %d-%d:" % (s_set_idx, s_idx))
                _p(6, 18, u"situationType", situation.situationType)
                for sm_idx, sm in enumerate(lun(situation.mentionList)):
                    print(u" " * 6 + u"SituationMention %d-%d-%d:" % (
                        s_set_idx, s_idx, sm_idx))
                    _print_situation_mention(sm)
                print()
            print()


def _print_situation_mention(situationMention):
    """
    Print SituationMention information needed to display both
    Situation and SituationMention types.

    Args:
        situationMention (SituationMention):
    """
    if situationMention.text:
        _p(10, 20, u"text", situationMention.text)
    if situationMention.situationType:
        _p(10, 20, u"situationType", situationMention.situationType)
    if situationMention.situationKind:
        _p(10, 20, u"situationKind", situationMention.situationKind)
    if situationMention.intensity:
        _p(10, 20, u"intensity", str(situationMention.intensity))
    for arg_idx, ma in enumerate(lun(situationMention.argumentList)):
        print(u" " * 10 + u"Argument %d:" % arg_idx)
        if ma.role:
            _p(14, 16, u"role", ma.role)
        if ma.entityMention:
            _p(14, 16, u"entityMention",
                u" ".join(_get_tokens_for_entityMention(ma.entityMention)))
        if ma.propertyList:
            # PROTO-ROLE PROPERTIES: Format a separate list for each
            # distinct annotator (metadata.tool) which tool should be
            # either None or a string. Sort by annotator
            # (metadata.tool) and then by property (p.value)
            last_tool = False
            for p in sorted(ma.propertyList,
                            key=lambda x: (x.metadata.tool, x.value)):
                tool = p.metadata.tool
                if tool != last_tool:
                    print(u" " * 14 + u"Properties (%s):" % tool)
                    last_tool = tool
                _p(18, 20, p.value, u"%1.1f" % p.polarity)
        # A SituationMention can have an argumentList with a
        # MentionArgument that points to another SituationMention---
        # which could conceivably lead to loops.  We currently don't
        # traverse the list recursively, instead looking at only
        # SituationMentions referenced by top-level SituationMentions
        if ma.situationMention:
            print(u" " * 14 + u"situationMention:")
            if situationMention.text:
                _p(18, 20, u"text", situationMention.text)
            if situationMention.situationType:
                _p(18, 20, u"situationType", situationMention.situationType)


def _p(indent_level, justified_width, fieldname, content):
    """
    Print field-value pair, indented and justified.

    Args:
        indent_level (int): number of spaces by which to prefix output
        justified_width (int): number of characters fieldname and colon
            should occupy (justified on left, padded with spaces)
        fieldname (str): field name
        content (str): field value
    """
    print(
        (u" " * indent_level) +
        (fieldname + u":").ljust(justified_width) +
        content
    )


def print_text_for_communication(comm, tool=None, communication_filter=None):
    """Print `text field of :class:`.Communication`

    Args:
        comm (Communication):
        tool (str): Deprecated.
                    If not `None`, only print `text` field of
                    :class:`.Communication` objects with a matching
                    `metadata.tool` field
        communication_filter (func): If not None, print information
            for only those :class:`.Communication` objects that pass
            this filter.  Should be a function that takes a list of
            annotations (objects with metadata fields) and returns a
            list of annotations (possibly filtered and re-ordered).
    """
    _filter = filter_unnone(tool_to_filter(tool, communication_filter))
    if _filter([comm]):
        print(comm.text)


def print_id_for_communication(comm, tool=None, communication_filter=None):
    """Print ID field of :class:`.Communication`

    Args:
        comm (Communication):
        tool (str): Deprecated.
                    If not `None`, only print ID of
                    :class:`.Communication` objects with a matching
                    `metadata.tool` field
        communication_filter (func): If not None, print information
            for only those :class:`.Communication` objects that pass
            this filter.  Should be a function that takes a list of
            annotations (objects with metadata fields) and returns a
            list of annotations (possibly filtered and re-ordered).

    """
    _filter = filter_unnone(tool_to_filter(tool, communication_filter))
    if _filter([comm]):
        print(comm.id)


def print_communication_taggings_for_communication(
        comm, tool=None, communication_tagging_filter=None):
    """Print information for :class:`.CommunicationTagging` objects

    Args:
        comm (Communication):
        tool (str): Deprecated.
                    If not `None`, only print information for
                    :class:`.CommunicationTagging` objects with a
                    matching `metadata.tool` field
        communication_tagging_filter (func): If not None, print information
            for only those :class:`.CommunicationTagging` objects that pass
            this filter.  Should be a function that takes a list of
            annotations (objects with metadata fields) and returns a
            list of annotations (possibly filtered and re-ordered).
    """
    _filter = filter_unnone(tool_to_filter(
        tool, communication_tagging_filter))
    for tagging in _filter(lun(comm.communicationTaggingList)):
        print('%s: %s' % (
            tagging.taggingType,
            ' '.join('%s:%.3f' % p for p in
                     zip(tagging.tagList, tagging.confidenceList))
        ))


def print_tokens_with_entityMentions(comm, tool=None, entity_mention_set_filter=None):
    """Print information for :class:`.Token` objects that are part of an :class:`.EntityMention`

    Args:
        comm (Communication):
        tool (str): Deprecated.
                    If not `None`, only print information for tokens
                    that are associated with an
                    :class:`.EntityMention` that is part of an
                    :class:`.EntityMentionSet` with a matching
                    `metadata.tool` field
        entity_mention_set_filter (func): If not None, print information
            for only those :class:`.EntityMentionSet` objects that pass
            this filter.  Should be a function that takes a list of
            annotations (objects with metadata fields) and returns a
            list of annotations (possibly filtered and re-ordered).
    """
    _filter = tool_to_filter(tool, entity_mention_set_filter)

    em_by_tkzn_id = _get_entityMentions_by_tokenizationId(
        comm, entity_mention_set_filter=_filter)
    em_entity_num = _get_entity_number_for_entityMention_uuid(
        comm, entity_mention_set_filter=_filter)
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
                print(u" ".join(text_tokens))
        print()


def print_tokens_for_communication(comm, tool=None, tokenization_filter=None):
    """Print token text for a :class:`.Communication`

    Args:
        comm (Communication):
        tool (str): Deprecated.
                    If not `None`, only print token text for
                    :class:`.Communication` objects with a matching
                    `metadata.tool` field
        tokenization_filter (func): If not None, print information
            for only those :class:`.Tokenization` objects that pass
            this filter.  Should be a function that takes a list of
            annotations (objects with metadata fields) and returns a
            list of annotations (possibly filtered and re-ordered).
    """
    tokenizations_by_section = _get_tokenizations_grouped_by_section(
        comm, tokenization_filter=tool_to_filter(tool, tokenization_filter))

    for tokenizations_in_section in tokenizations_by_section:
        for tokenization in tokenizations_in_section:
            if tokenization.tokenList:
                text_tokens = [token.text
                               for token
                               in tokenization.tokenList.tokenList]
                print(u" ".join(text_tokens))
        print()


def print_penn_treebank_for_communication(comm, tool=None, parse_filter=None):
    """Print Penn-Treebank parse trees for all :class:`.Tokenization` objects

    Args:
        comm (Communication):
        tool (str): Deprecated.
                    If not `None`, only print information for
                    :class:`.Tokenization` objects with a matching
                    `metadata.tool` field
        parse_filter (func): If not None, print information
            for only those :class:`.Parse` objects that pass
            this filter.  Should be a function that takes a list of
            annotations (objects with metadata fields) and returns a
            list of annotations (possibly filtered and re-ordered).
    """
    _filter = filter_unnone(tool_to_filter(tool, parse_filter))
    for tokenization in get_tokenizations(comm):
        for parse in _filter(lun(tokenization.parseList)):
            print(penn_treebank_for_parse(parse) + u"\n\n")


def penn_treebank_for_parse(parse):
    """
    Return a Penn-Treebank style representation of a Parse object

    Args:
        parse (Parse):

    Returns:
        str: A string containing a Penn Treebank style parse tree
        representation
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
    '''
    Return list of `comm.text` substrings corresponding to the tokens in
    :class:`.Tokenization` `tokenization` (where tokens without
    `textSpan` fields are represented by None in the output list), or
    return None if `tokenization` is None.

    Args:
        comm (Communication):
        tokenization (Tokenization):
    '''
    if tokenization.tokenList:
        char_offset_tags = [None] * len(tokenization.tokenList.tokenList)

        if comm.text:
            for i, token in enumerate(tokenization.tokenList.tokenList):
                if token.textSpan:
                    char_offset_tags[i] = comm.text[
                        token.textSpan.start:token.textSpan.ending]
        return char_offset_tags


def _sorted_dep_lists_for_tokenization(tokenization,
                                       dependency_parse_filter=None):
    """
    Return list of lists of dependencies whose parses match the provided
    annotation filter.  Each list of dependencies has length
    is equal to the number of tokens in this tokenization's token list,
    where the element at index i is a dependency if there is a
    dependency whose dep field is i and None otherwise.

    Args:
        tokenization (Tokenization):
        dependency_parse_filter (func): If not None, ignore
            those :class:`.DependencyParse` objects that do not pass
            this filter.  Should be a function that takes a list of
            annotations (objects with metadata fields) and returns a
            list of annotations (possibly filtered and re-ordered).
    """
    _filter = filter_unnone(dependency_parse_filter)

    def _dep_lists():
        if tokenization.tokenList is not None:
            for dependency_parse in _filter(tokenization.dependencyParseList):
                sorted_dep_list = [None] * len(tokenization.tokenList.tokenList)
                for dep in dependency_parse.dependencyList:
                    sorted_dep_list[dep.dep] = dep
                yield sorted_dep_list

    return list(_dep_lists())


def _get_conll_tags_for_tokenization(tokenization, dependency_parse_filter=None):
    """
    Return a list of lists of CoNLL 'HEAD' and 'DEPREL' tag pairs for a
    tokenization

    In the CoNLL data format:

        http://ufal.mff.cuni.cz/conll2009-st/task-description.html

    the HEAD for a token is the (1-indexed) index of that token's
    parent token.  The root token of the dependency parse has a HEAD
    index of 0.

    Args:
        tokenization (Tokenization):
        dependency_parse_filter (func): If not None, ignore
            those :class:`.DependencyParse` objects that do not pass
            this filter.  Should be a function that takes a list of
            annotations (objects with metadata fields) and returns a
            list of annotations (possibly filtered and re-ordered).

    Returns:
        list: A list of lists of pairs, each of which contains a
              CoNLL HEAD tag and CoNLL DEPREL tag (as strings), one
              pair for each token in the supplied tokenization.  If a
              token does not have a HEAD tag (e.g. punctuation
              tokens), the HEAD tag is an empty string.  If a token
              does not have a DEPREL tag (e.g. punctuation tokens),
              the DEPREL tag is an empty string.
    """
    return [
        list(map(
            lambda dep: (
                unicode(
                    '' if dep is None else (
                        0 if dep.gov is None else dep.gov + 1
                    )
                ),
                unicode(
                    '' if dep is None else (
                        '' if dep.edgeType is None else dep.edgeType
                    )
                ),
            ),
            dep_list
        ))
        for dep_list in _sorted_dep_lists_for_tokenization(
            tokenization,
            dependency_parse_filter=dependency_parse_filter)
    ]


def _get_entityMentions_by_tokenizationId(comm, entity_mention_set_filter=None):
    """
    Return entity mentions for a Communication grouped by Tokenization
    UUID string

    Args:
        comm (Communication):
        entity_mention_set_filter (func): If not None, ignore
            those :class:`.EntityMentionSet` objects that do not pass
            this filter.  Should be a function that takes a list of
            annotations (objects with metadata fields) and returns a
            list of annotations (possibly filtered and re-ordered).

    Returns:
        A dictionary of lists of EntityMentions, where the dictionary
        keys are Tokenization UUID strings.
    """
    _filter = filter_unnone(entity_mention_set_filter)
    mentions_by_tkzn_id = defaultdict(list)
    for entitySet in lun(comm.entitySetList):
        for entity in entitySet.entityList:
            for entityMention in entity.mentionList:
                if _filter([entityMention.entityMentionSet]):
                    u = entityMention.tokens.tokenizationId.uuidString
                    mentions_by_tkzn_id[u].append(entityMention)
    return mentions_by_tkzn_id


def _get_entity_number_for_entityMention_uuid(comm, entity_mention_set_filter=None):
    """Create mapping from EntityMention UUID to (zero-indexed)
    'Entity Number'

    Args:
        comm (Communication):
        entity_mention_set_filter (func): If not None, ignore
            those :class:`.EntityMentionSet` objects that do not pass
            this filter.  Should be a function that takes a list of
            annotations (objects with metadata fields) and returns a
            list of annotations (possibly filtered and re-ordered).

    Returns:
        A dictionary where the keys are EntityMention UUID strings,
        and the values are "Entity Numbers", where the first Entity is
        assigned number 0, the second Entity is assigned number 1,
        etc.
    """
    _filter = filter_unnone(entity_mention_set_filter)
    entity_number_for_entityMention_uuid = {}
    entity_number_counter = 0

    if comm.entitySetList:
        for entitySet in comm.entitySetList:
            for entity in entitySet.entityList:
                any_mention = False
                for entityMention in entity.mentionList:
                    if _filter([entityMention.entityMentionSet]):
                        entity_number_for_entityMention_uuid[
                            entityMention.uuid.uuidString
                        ] = entity_number_counter
                    any_mention = True
                if any_mention:
                    entity_number_counter += 1
    return entity_number_for_entityMention_uuid


def _get_tokenizations_grouped_by_section(comm, tokenization_filter=None):
    """
    Return a list of lists of Tokenization objects in a Communication

    Args:
        comm (Communication):
        tokenization_filter (func): If not None, ignore
            those :class:`.Tokenization` objects that do not pass
            this filter.  Should be a function that takes a list of
            annotations (objects with metadata fields) and returns a
            list of annotations (possibly filtered and re-ordered).

    Returns:
        Returns a list of lists of Tokenization objects, where the
        Tokenization objects are grouped by Section
    """
    _filter = filter_unnone(tokenization_filter)

    return [
        _filter([
            sentence.tokenization
            for sentence in lun(section.sentenceList)
        ])
        for section in lun(comm.sectionList)
    ]


def _get_tokens_for_entityMention(entityMention):
    """
    Return list of token strings for an EntityMention

    Args:
        entityMention (EntityMention):

    Returns:
        A list of token strings
    """
    tokens = []
    for tokenIndex in entityMention.tokens.tokenIndexList:
        tokens.append(entityMention.tokens.tokenization.tokenList.tokenList[
                      tokenIndex].text)
    return tokens
