"""Add reference variables for each :class:`.UUID` "pointer" in a
:class:`.Communication`

"""
from __future__ import unicode_literals


def add_references_to_communication(comm):
    """Create references for each :class:`.UUID` 'pointer'

    Args:
        comm (Communication): A Concrete Communication object

    The Concrete schema uses :class:`.UUID` objects as internal
    pointers between Concrete objects.  This function adds member
    variables to Concrete objects that are references to the Concrete
    objects identified by the :class:`.UUID`.

    For example, each :class:`.Entity` has a `mentionIdlist` that
    lists the UUIDs of the :class:`.EntityMention` objects for that
    :class:`.Entity`.  This function adds a `mentionList` variable
    to the :class:`.Entity` that is a list of references to the
    actual :class:`.EntityMention` objects.  This allows you to
    access the :class:`.EntityMention` objects using:

        entity.mentionList

    This function adds these reference variables:

    - `tokenization` to each :class:`.TokenRefSequence`
    - `entityMention` to each :class:`.Argument`
    - `sentence` backpointer to each :class:`.Tokenization`
    - `parentMention` backpointer to appropriate :class:`.EntityMention`

    And adds these lists of reference variables:

    - `mentionList` to each :class:`.Entity`
    - `situationMention` to each :class:`.Argument`
    - `mentionList` to each :class:`.Situation`
    - `childMentionList` to each :class:`.EntityMention`

    For variables that represent optional lists of :class:`.UUID`
    objects (e.g. `situation.mentionIdList`), Python Thrift will set
    the variable to `None` if the list is not provided.  When this
    function adds a list-of-references variable (in this case,
    `situation.mentionList`) for an *omitted* optional list, it sets
    the new variable to `None` - it **DOES NOT** leave the variable
    undefined.

    """
#    comm.dependencyParseForUUID = {}
    comm.entityForUUID = {}
    comm.entityMentionForUUID = {}
#    comm.parseForUUID = {}
    comm.sectionForUUID = {}
    comm.sentenceForUUID = {}
    comm.situationForUUID = {}
    comm.situationMentionForUUID = {}
    comm.tokenizationForUUID = {}
#    comm.tokenTaggingForUUID = {}

    if comm.sectionList:
        for section in comm.sectionList:
            comm.sectionForUUID[section.uuid.uuidString] = section
            if section.sentenceList:
                for sentence in section.sentenceList:
                    comm.sentenceForUUID[sentence.uuid.uuidString] = sentence
                    if sentence.tokenization:
                        comm.tokenizationForUUID[
                            sentence.tokenization.uuid.uuidString] = \
                            sentence.tokenization
                        sentence.tokenization.sentence = sentence

    if comm.entityMentionSetList:
        for entityMentionSet in comm.entityMentionSetList:
            for entityMention in entityMentionSet.mentionList:
                comm.entityMentionForUUID[entityMention.uuid.uuidString] = \
                    entityMention
                try:
                    entityMention.tokens.tokenization = \
                        comm.tokenizationForUUID[
                            entityMention.tokens.tokenizationId.uuidString]
                except KeyError:
                    entityMention.tokens.tokenization = None
                # childMentionList and parentMention are in-memory references,
                # and not part of the Concrete schema
                entityMention.childMentionList = []
                entityMention.parentMention = None
                entityMention.entityMentionSet = entityMentionSet
            for entityMention in entityMentionSet.mentionList:
                if entityMention.childMentionIdList:
                    for childMentionId in entityMention.childMentionIdList:
                        childMention = comm.entityMentionForUUID[
                            childMentionId.uuidString]
                        childMention.parentMention = entityMention
                        entityMention.childMentionList.append(childMention)

    if comm.entitySetList:
        for entitySet in comm.entitySetList:
            for entity in entitySet.entityList:
                comm.entityForUUID[entity.uuid.uuidString] = entity
                entity.mentionList = []
                for mentionId in entity.mentionIdList:
                    entity.mentionList.append(
                        comm.entityMentionForUUID[mentionId.uuidString])
                entity.entitySet = entitySet

    if comm.situationMentionSetList:
        for situationMentionSet in comm.situationMentionSetList:
            for situationMention in situationMentionSet.mentionList:
                comm.situationMentionForUUID[situationMention.uuid.uuidString]\
                    = situationMention
                for argument in situationMention.argumentList:
                    if argument.entityMentionId:
                        argument.entityMention = comm.entityMentionForUUID[
                            argument.entityMentionId.uuidString]
                    else:
                        argument.entityMention = None
                    if argument.situationMentionId:
                        argument.situationMention = \
                            comm.situationMentionForUUID[
                                argument.situationMentionId.uuidString]
                    else:
                        argument.situationMention = None
                    if argument.tokens:
                        argument.tokens.tokenization = \
                            comm.tokenizationForUUID[
                                argument.tokens.tokenizationId.uuidString]
                if situationMention.tokens:
                    try:
                        situationMention.tokens.tokenization = \
                            comm.tokenizationForUUID[
                                situationMention.tokens.
                                tokenizationId.uuidString
                            ]
                    except KeyError:
                        situationMention.tokens.tokenization = None
                situationMention.situationMentionSet = situationMentionSet

    if comm.situationSetList:
        for situationSet in comm.situationSetList:
            for situation in situationSet.situationList:
                comm.situationForUUID[situation.uuid.uuidString] = situation
                if situation.mentionIdList:
                    situation.mentionList = []
                    for mentionId in situation.mentionIdList:
                        situation.mentionList.append(
                            comm.situationMentionForUUID[mentionId.uuidString])
                else:
                    situation.mentionList = None
                situation.situationSet = situationSet
