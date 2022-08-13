Advanced Usage
==============

In this section we demonstrate more advanced processing of Concrete
Communications.  We previously traversed Sections, Sentences,
TokenLists, and TokenTaggings, which have a nested linear structure; we
now demonstrate usage of DependencyParses, Entities, and
SituationMentions, which are non-linear, higher-level annotations.

Print DependencyParses
----------------------

The following code prints a Communication's tokens and their dependency
graph in CoNLL format, similar to ``concrete-inspect.py --dependency``,
for the first dependency parse in each sentence.  This example makes
use of serif_dog-bites-man.concrete_::

    from concrete.util import read_communication_from_file, lun
    comm = read_communication_from_file('serif_dog-bites-man.concrete')

    for section in lun(comm.sectionList):
        for sentence in lun(section.sentenceList):
            if sentence.tokenization and sentence.tokenization.tokenList:
                # Columns of CoNLL-style output go here.
                taggings = []

                # Token text
                taggings.append([x.text for x in sentence.tokenization.tokenList.tokenList])

                if sentence.tokenization.dependencyParseList:
                    # Read dependency arcs from dependency parse tree. (Deps start at zero.)
                    head = [-1]*len(sentence.tokenization.tokenList.tokenList)
                    for arc in sentence.tokenization.dependencyParseList[0].dependencyList:
                        head[arc.dep] = arc.gov

                    # Add head index to taggings
                    taggings.append(head)

                # Transpose the list. Format and print each row.
                for row in zip(*taggings):
                    print('\t'.join('%15s' % x for x in row))

                print('')

There are many optional fields in Concrete and here we've encountered
several of them: ``Communication.sectionList``,
``Section.sentenceList``, ``Sentence.tokenization``,
``Tokenization.tokenList``, and ``Tokenization.dependencyParseList``.
An unset optional field is represented with a value of ``None``.
We've used :py:func:`concrete.util.unnone.lun`, which returns its
argument if its argument is not ``None`` and otherwise returns an empty
list, to work around some of the optional fields, while we've directly
checked the others.

Expected output of the previous code::

               John	              1
              Smith	              9
                  ,	             -1
            manager	              1
                 of	              6
               ACMÉ	              6
                INC	              3
                  ,	             -1
                was	              9
                bit	             -1
                 by	             12
                  a	             12
                dog	              9
                 on	             14
              March	             12
               10th	             14
                  ,	             -1
               2013	             12
                  .	             -1

                 He	              1
               died	             -1
                  !	             -1

               John	              2
                 's	              0
           daughter	              4
               Mary	              4
          expressed	             -1
             sorrow	              4
                  .	             -1




Print Entities
--------------

We now print Entities and their EntityMentions (which represent the
result of coreference resolution).  This example makes use of
serif_dog-bites-man.concrete_::

    from concrete.util import read_communication_from_file, lun
    comm = read_communication_from_file('serif_dog-bites-man.concrete')

    for entitySet in lun(comm.entitySetList):
        for ei, entity in enumerate(entitySet.entityList):
            print('Entity %s (%s)' % (ei, entity.canonicalName))
            for i, mention in enumerate(entity.mentionList):
                print('  Mention %s: %s' % (i, mention.text))
            print('')
        print('')

Note that ``Entity.mentionList`` is `not in the schema`_!  This field
was added in
:py:func:`concrete.util.file_io.read_communication_from_file` after
deserializing the original Communication.  By default, some additional
fields are added to Concrete objects by
:py:func:`concrete.util.references.add_references_to_communication`
when they are deserialized; see that function's documentation for
details.  For our purposes here, know that
``add_references_to_communication`` adds a ``mentionList`` field to
each Entity that contains a list of the EntityMentions that reference
that Entity.

Expected output of the previous code::

    Entity 0 (None)
      Mention 0: John Smith
      Mention 1: John Smith, manager of ACMÉ INC,
      Mention 2: manager of ACMÉ INC
      Mention 3: He
      Mention 4: John

    Entity 1 (None)
      Mention 0: ACMÉ INC

    Entity 2 (None)
      Mention 0: John's daughter Mary
      Mention 1: daughter


    Entity 0 (2013-03-10)
      Mention 0: March 10th, 2013





Print SituationMentions
-----------------------

We now print SituationMentions, the results of relation extraction.
This example makes use of serif_example.concrete_, on which BBN-SERIF's
relation and event extractor has been run::

    from concrete.util import read_communication_from_file, lun
    comm = read_communication_from_file('serif_example.concrete')

    for i, situationMentionSet in enumerate(lun(comm.situationMentionSetList)):
        if situationMentionSet.metadata:
            print('Situation Set %d (%s):' % (i, situationMentionSet.metadata.tool))
        else:
            print('Situation Set %d:' % i)
        for j, situationMention in enumerate(situationMentionSet.mentionList):
            print('SituationMention %d-%d:' % (i, j))
            print('    text', situationMention.text)
            print('    situationType', situationMention.situationType)
            for k, arg in enumerate(lun(situationMention.argumentList)):
                print('    Argument %d:' % k)
                print('      role', arg.role)
                if arg.entityMention:
                    print('      entityMention', arg.entityMention.text)
                if arg.situationMention:
                    print('      situationMention:')
                    print('        text', situationMention.text)
                    print('        situationType', situationMention.situationType)
            print('')
        print('')

Expected output::

    Situation Set 0 (Serif: relations):
    SituationMention 0-0:
        text None
        situationType ORG-AFF.Employment
        Argument 0:
          role Role.RELATION_SOURCE_ROLE
          entityMention manager of ACME INC
        Argument 1:
          role Role.RELATION_TARGET_ROLE
          entityMention ACME INC

    SituationMention 0-1:
        text None
        situationType PER-SOC.Family
        Argument 0:
          role Role.RELATION_SOURCE_ROLE
          entityMention John
        Argument 1:
          role Role.RELATION_TARGET_ROLE
          entityMention daughter


    Situation Set 1 (Serif: events):
    SituationMention 1-0:
        text died
        situationType Life.Die
        Argument 0:
          role Victim
          entityMention He





.. _serif_dog-bites-man.concrete: https://github.com/hltcoe/concrete-python/raw/main/tests/testdata/serif_dog-bites-man.concrete
.. _serif_example.concrete: https://github.com/hltcoe/quicklime/raw/master/serif_example.concrete
.. _`not in the schema`: http://hltcoe.github.io/concrete/schema/entities.html#Struct_Entity
