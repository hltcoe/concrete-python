"""Add reference variables for each UUID "pointer" in a Communication
"""


def add_references_to_communication(comm):
    """Create references for each UUID 'pointer'

    Args:

    - `comm`: A Concrete Communication object

    -----

    The Concrete schema uses UUIDs as internal pointers between
    Concrete objects.  This function adds member variables to Concrete
    objects that are references to the Concrete objects identified by
    the UUIDs.

    For example, each Entity has a `mentionIdlist` that lists the
    UUIDs of the EntityMentions for that Entity.  This function adds a
    `mentionList` variable to the Entity that is a list of references
    to the actual EntityMention objects.  This allows you to access
    the EntityMentions using:

        entity.mentionList

    This function adds these reference variables:

    - `tokenization` to each TokenRefSequence
    - `entityMention` to each Argument
    - `sentence` backpointer to each Tokenization
    - `parentMention` backpointer to appropriate EntityMention

    And adds these lists of reference variables:

    - `mentionList` to each Entity
    - `situationMention` to each Argument
    - `mentionList` to each Situation
    - `childMentionList` to each EntityMention

    For variables that represent optional lists of UUIDs
    (e.g. `situation.mentionIdList`), Python Thrift will set the
    variable to `None` if the list is not provided.  When this function
    adds a list-of-references variable (in this case,
    `situation.mentionList`) for an *omitted* optional list, it sets the
    new variable to `None` - it **DOES NOT** leave the variable undefined.
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
