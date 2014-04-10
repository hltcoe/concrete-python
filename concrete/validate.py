"""
Libary to (partially) validate a Concrete Communication

Current validation checks:
  - do all sentenceSegmentation.sectionId's match the uuid of the
    enclosing section?
  - for each constituent parse, do any of the constituent ID's for
    that parse repeat?
  - is each dependency and constituent parse a fully connected graph?
  - is each dependency and constituent parse "tree" really a tree?
  - for each dependency parse, are there any nodes with a null
    governer node whose edgeType is not root?
  - for each entityMention, does entityMention.tokens.tokenizationId
    point to a valid tokenization uuid?
  - for each entity, do all the entity's entityMentionId's point to a
    valid entityMention uuid?


TODO: Validate...
  - Situation.mentionIdList
  - Argument.entityId
  - Argument.situationId
  - Justification.mentionId
"""

import logging

import networkx as nx
from thrift import TSerialization
from thrift.protocol import TProtocol
from thrift.Thrift import TType

from concrete import Communication



def validate_communication_file(communication_filename):
    logging.info(ilm(0, "Opening Concrete Communication with filename '%s'" % communication_filename))
    comm = Communication()
    comm_bytestring = open(communication_filename).read()
    TSerialization.deserialize(comm, comm_bytestring)
    validate_communication(comm)


def validate_communication(comm):
    """
    Args:
      comm (concrete.structure.ttypes.Communication)

    Returns:
      bool: True if Communication is valid, False otherwise
    """
    valid = True

    logging.info(ilm(0, "Validating Communication with ID '%s'" % comm.id))

    valid &= validate_thrift_object_required_fields_recursively(comm)

    if comm.sectionSegmentations:
        logging.debug(ilm(1, "Communication '%s' has %d sectionSegmentations" %
                          (comm.id, len(comm.sectionSegmentations))))
        for sectionSegmentation in comm.sectionSegmentations:
            logging.debug(ilm(2, "sectionSegmentation '%s' has %d sections" %
                              (sectionSegmentation.uuid, len(sectionSegmentation.sectionList))))
            for section in sectionSegmentation.sectionList:
                if section.sentenceSegmentation:
                    logging.debug(ilm(3, "section '%s' has %d sentenceSegmentations" %
                                      (section.uuid, len(section.sentenceSegmentation))))
                    for sentenceSegmentation in section.sentenceSegmentation:
                        logging.debug(ilm(4, "sentenceSegmentation '%s' has %d sentences" %
                                          (sentenceSegmentation.uuid, len(sentenceSegmentation.sentenceList))))
                        if sentenceSegmentation.sectionId != section.uuid:
                            valid = False
                            logging.error(ilm(5, "sentenceSegmentation.sectionId '%s' does not match section.uuid '%s'" %
                                              (sentenceSegmentation.sectionId, sentenceSegmentation.uuid)))
                        for sentence in sentenceSegmentation.sentenceList:
                            logging.debug(ilm(5, "sentence '%s' has %d tokenizations" %
                                              (sentence.uuid, len(sentence.tokenizationList))))
                            for tokenization in sentence.tokenizationList:
                                valid &= validate_constituency_parse(tokenization)
                                valid &= validate_dependency_parses(tokenization)

    valid &= validate_entity_mention_ids(comm)
    valid &= validate_entity_mention_tokenization_ids(comm)

    if not valid:
        logging.error(ilm(0, "The Communication with ID '%s' IS NOT valid" % comm.id))
    else:
        logging.info(ilm(0, "The Communication with ID '%s' is valid" % comm.id))

    return valid


def get_entity_mention_uuid_set(comm):
    """
    Args:
      comm (concrete.structure.ttypes.Communication)

    Returns:
      set of ints: UUIDs for all EntityMentions in the Communication
    """
    entity_mention_uuid_set = set()
    if comm.entityMentionSets:
        for entityMentionSet in comm.entityMentionSets:
            if entityMentionSet.mentionSet:
                for entityMention in entityMentionSet.mentionSet:
                    entity_mention_uuid_set.add(entityMention.uuid)
    return entity_mention_uuid_set


def get_tokenization_uuid_set(comm):
    """
    Args:
      comm (concrete.structure.ttypes.Communication)

    Returns:
      set of ints: UUIDs for all Tokenizations in the Communication
    """
    tokenization_uuid_set = set()
    if comm.sectionSegmentations:
        for sectionSegmentation in comm.sectionSegmentations:
            for section in sectionSegmentation.sectionList:
                if section.sentenceSegmentation:
                    for sentenceSegmentation in section.sentenceSegmentation:
                        for sentence in sentenceSegmentation.sentenceList:
                            for tokenization in sentence.tokenizationList:
                                tokenization_uuid_set.add(tokenization.uuid)
    return tokenization_uuid_set


def ilm(indent_level, log_message):
    """
    ilm = Indented Log Message

    Prepend spaces to a log message so that log messages can be
    printed in a hierarchical list

    Args:
      log_message (string): Log message tob e indented
      indent_level (int): Indentation level

    Returns:
      string: Indented log message
    """
    return "  " * indent_level + log_message


def validate_constituency_parse(tokenization):
    """
    Args:
      tokenization (concrete.structure.ttypes.Tokenization)

    Returns:
      bool: True if tokenization's constituency parse is valid, False otherwise
    """
    valid = True

    total_constituents = len(tokenization.parse.constituentList)
    logging.debug(ilm(6, "tokenization '%s' has %d constituents" % (tokenization.uuid, total_constituents)))

    total_uuid_mismatches = 0
    constituent_id_set = set()
    constituent_parse_tree = nx.DiGraph()

    for constituent in tokenization.parse.constituentList:
        # Add nodes to parse tree
        constituent_parse_tree.add_node(constituent.id)

        if constituent.id not in constituent_id_set:
            constituent_id_set.add(constituent.id)
        else:
            valid = False
            logging.error(ilm(7, "constituent ID %d has already been used in this sentence's tokenization" % constituent.id))

        # Per the Concrete 'structure.thrift' file, tokenSequence may not be defined:
        #   "Typically, this field will only be defined for leaf constituents (i.e., constituents with no children)."
        if constituent.tokenSequence and constituent.tokenSequence.tokenizationId != tokenization.uuid:
            total_uuid_mismatches += 1

    if total_uuid_mismatches > 0:
        valid = False
        logging.error(ilm(6, "tokenization '%s' has UUID mismatch for %d/%d constituents" %
                          (tokenization.uuid, total_uuid_mismatches, total_constituents)))

    # Add edges to constituent parse tree
    for constituent in tokenization.parse.constituentList:
        if constituent.childList:
            for child_id in constituent.childList:
                constituent_parse_tree.add_edge(constituent.id, child_id)

    # Check if constituent parse "tree" is actually a tree
    undirected_graph = constituent_parse_tree.to_undirected()
    if not nx.is_connected(undirected_graph):
        valid = False
        logging.error(ilm(6, "The constituent parse \"tree\" is not a fully connected graph - the graph has %d components" %
            len(nx.connected_components(undirected_graph))))
    if nx.number_of_nodes(constituent_parse_tree) != nx.number_of_edges(constituent_parse_tree) + 1:
        valid = False
        logging.error(ilm(6, "The constituent parse \"tree\" is not a tree.  |V| != |E|+1  (|V|=%d, |E|=%d)" %
            (nx.number_of_nodes(constituent_parse_tree), nx.number_of_edges(constituent_parse_tree))))

    return valid


def validate_dependency_parses(tokenization):
    """
    Args:
      tokenization (concrete.structure.ttypes.Tokenization)

    Returns:
      bool: True if all of a tokenization's dependency parses are valid, False otherwise
    """
    valid = True

    # Verify that each dependency parse "tree" is actually a tree
    if tokenization.dependencyParseList:
        for dependencyParse in tokenization.dependencyParseList:
            dependency_parse_tree = nx.DiGraph()

            # Add nodes to dependency parse tree
            for dependency in dependencyParse.dependencyList:
                if dependency.gov is None and dependency.edgeType != "root":
                    valid = False
                    logging.error(ilm(6, "Found a null dependency parse node with governer whose edgeType is '%s' instead of 'root'" %
                                          dependency.edgeType))
                if dependency.gov is not None:
                    dependency_parse_tree.add_node(dependency.gov)
                dependency_parse_tree.add_node(dependency.dep)

            # Add edges to dependency parse tree
            for dependency in dependencyParse.dependencyList:
                if dependency.gov is not None:
                    dependency_parse_tree.add_edge(dependency.gov, dependency.dep)

            # Check if dependency parse tree is actually a tree
            undirected_graph = dependency_parse_tree.to_undirected()
            if not nx.is_connected(undirected_graph):
                valid = False
                logging.error(ilm(6, "The dependency parse \"tree\" is not a fully connected graph - the graph has %d components" %
                                      len(nx.connected_components(undirected_graph))))
    return valid


def validate_entity_mention_ids(comm):
    valid = True
    entity_mention_uuid_set = get_entity_mention_uuid_set(comm)

    if comm.entitySets:
        for entitySet in comm.entitySets:
            if entitySet.entityList:
                for entity in entitySet.entityList:
                    for entityMentionId in entity.mentionIdList:
                        if entityMentionId not in entity_mention_uuid_set:
                            valid = False
                            logging.error(ilm(2, "Entity '%s' has an invalid entityMentionId (%s)" % (entity.uuid, entityMentionId)))
    return valid


def validate_entity_mention_tokenization_ids(comm):
    valid = True
    entity_mention_uuid_set = get_entity_mention_uuid_set(comm)
    tokenization_uuid_set = get_tokenization_uuid_set(comm)

    if comm.entityMentionSets:
        for entityMentionSet in comm.entityMentionSets:
            if entityMentionSet.mentionSet:
                for entityMention in entityMentionSet.mentionSet:
                    if entityMention.tokens.tokenizationId not in tokenization_uuid_set:
                        valid = False
                        logging.error(ilm(2, "Mention '%s' has an invalid tokenizationId (%s)" % (entityMention.uuid, entityMention.tokens.tokenizationId)))
    return valid


def validate_thrift_object_required_fields(thrift_object, indent_level=0):
    """
    Test if a thrift object has all required fields.

    This function calls the thrift object's validate() function, and
    if an exception is raised because of missing required fields, the
    function catches the exception and logs the exception error
    message.

    Args:
      thrift_object

    Returns:
      bool: True if the thrift object has all required fields, False otherwise
    """
    try:
        thrift_object.validate()
    except TProtocol.TProtocolException as e:
        thrift_object_name = str(thrift_object.__class__).split('.')[-1].split("'")[0]
        if hasattr(thrift_object, 'uuid') and thrift_object.uuid is not None:
            thrift_object_name += " '%s'" % thrift_object.uuid
        # For readability, add quotes around field name, changing:
        #   Required field id is unset!
        # to:
        #   Required field 'id' is unset!
        em = e.message.replace("Required field ", "Required Field '").replace(" is unset", "' is unset")
        logging.error(ilm(indent_level, "%s: %s" % (thrift_object_name, em)))
        return False
    else:
        return True



########################################################################################################
# The Python version of Thrift 0.9.1 does not support deep (recursive)
# validation, and none of the Thrift serialization/deserialization
# code calls even the shallow validation functions provided by Thrift.
#
# The code below implements deep validation.  The code is adapted from:
#
#   https://raw.githubusercontent.com/flamholz/py-thrift-validation-example/master/util/validation.py
#
# See this blog post for more information:
#
#   http://techblog.ridewithvia.com/post/38231652492/recursive-validation-of-python-thrift-structures
#
# A patch to implement deep validation was submitted to the Thrift
# repository in February of 2013:
#
#   https://issues.apache.org/jira/browse/THRIFT-1732
#
# but Thrift 0.9.1 - which was released on 2013-08-21 - does not
# include this functionality.

RECURSE_ON = frozenset([TType.STRUCT,
                        TType.LIST,
                        TType.MAP,
                        TType.SET])

def _ShouldRecurse(ttype):
    """Returns True if this ttype is one we recurse on for validation."""
    return ttype in RECURSE_ON

def validate_thrift_object_required_fields_recursively(msg, indent_level=0, valid=True):
    """Deep validation of thrift messages.

    Args:
        msg: a Thrift message.
    """
    assert msg is not None
    valid &= validate_thrift_object_required_fields(msg, indent_level)

    # Introspect the structure specification.
    # For each field, check type and decide whether to recurse.
    spec = msg.thrift_spec
    for spec_tuple in spec:
        if spec_tuple is None:
            continue

        mtype = spec_tuple[1]
        name = spec_tuple[2]
        attr = getattr(msg, name)
        if not _ShouldRecurse(mtype):
            # Some primitive type that we don't validate.
            continue

        # Fetch the item itself.
        if attr is None:
            continue

        # Field is set and it's a message or collection, so we validate.
        if mtype == TType.STRUCT:
            valid &= validate_thrift_object_required_fields_recursively(attr, indent_level+1, valid)
        elif mtype in (TType.LIST, TType.SET):
            subtype = spec_tuple[3][0]
            if _ShouldRecurse(subtype):
                for submsg in attr:
                    valid &= validate_thrift_object_required_fields_recursively(submsg, indent_level+1, valid)
        elif mtype == TType.MAP:
            subtype = spec_tuple[3]
            key_type = subtype[0]
            val_type = subtype[2]
            for key, val in attr.iteritems():
                if _ShouldRecurse(key_type):
                    valid &= validate_thrift_object_required_fields_recursively(key, indent_level+1, valid)
                if _ShouldRecurse(val_type):
                    valid &= validate_thrift_object_required_fields_recursively(val, indent_level+1, valid)

    return valid
########################################################################################################
