Tutorial
========

.. image:: https://travis-ci.org/hltcoe/concrete-python.svg
   :target: https://travis-ci.org/hltcoe/concrete-python
.. image:: https://ci.appveyor.com/api/projects/status/0346c3lu11vj8xqj?svg=true
   :target: https://ci.appveyor.com/project/cjmay/concrete-python-f3iqf


Concrete-python is the Python interface to Concrete_, a
natural language processing data format and set of service protocols
that work across different operating systems and programming languages
via `Apache Thrift`_.  Concrete-python contains generated Python
classes, utility classes and functions, and scripts.  It does not contain the
Thrift schema for Concrete, which can be found in the
`Concrete GitHub repository`_.

For information about installing and using concrete-python, please see the
`online documentation`_.


.. contents:: **Table of Contents**
   :local:
   :backlinks: none


License
-------

Copyright 2012-2017 Johns Hopkins University HLTCOE. All rights
reserved.  This software is released under the 2-clause BSD license.
Please see LICENSE_ for more information.


Requirements
------------

concrete-python is tested on Python 2.7 or 3.5 (it does not run on
Python 2.6; it may run on more Python 3.x versions) and requires the
Thrift Python library, among other Python libraries.  These are
installed automatically by ``setup.py`` or ``pip``.  The Thrift
compiler is *not* required.

**Note**: The accelerated protocol offers a (de)serialization speedup
of 10x or more; if you would like to use it, ensure a C++ compiler is
available on your system before installing concrete-python.
(If a compiler is not available, concrete-python will fall back to the
unaccelerated protocol automatically.)  If you are on Linux, a suitable
C++ compiler will be listed as ``g++`` or ``gcc-c++`` in your package
manager.


Installation
------------

You can install Concrete using the ``pip`` package manager::

    pip install concrete

or by cloning the repository and running ``setup.py``::

    git clone https://github.com/hltcoe/concrete-python.git
    cd concrete-python
    python setup.py install


Basic usage
-----------

Here and in the following sections we make use of an example Concrete
Communication file included in the concrete-python source distribution.
The *Communication* type represents an article, book, post, Tweet, or
any other kind of document that we might want to store and analyze.
Copy it from ``tests/testdata/serif_dog-bites-man.concrete`` if you
have the concrete-python source distribution or download it
separately here: serif_dog-bites-man.concrete_.

First we use the ``concrete-inspect.py`` tool (explained in more detail
in the following section) to inspect some of the contents of the
Communication::

    concrete-inspect.py --text serif_dog-bites-man.concrete

This command prints the text of the Communication to the console.  In
our case the text is a short article formatted in SGML::

    <DOC id="dog-bites-man" type="other">
    <HEADLINE>
    Dog Bites Man
    </HEADLINE>
    <TEXT>
    <P>
    John Smith, manager of ACMÉ INC, was bit by a dog on March 10th, 2013.
    </P>
    <P>
    He died!
    </P>
    <P>
    John's daughter Mary expressed sorrow.
    </P>
    </TEXT>
    </DOC>

Now run the following command to inspect some of the annotations stored
in that Communication::

    concrete-inspect.py --ner --pos --dependency serif_dog-bites-man.concrete

This command shows a tokenization, part-of-speech tagging, named entity
tagging, and dependency parse in a CoNLL_-like columnar format::

    INDEX	TOKEN	POS	NER	HEAD	DEPREL
    -----	-----	---	---	----	------
    1	John	NNP	PER	2	compound
    2	Smith	NNP	PER	10	nsubjpass
    3	,	,			
    4	manager	NN		2	appos
    5	of	IN		7	case
    6	ACMÉ	NNP	ORG	7	compound
    7	INC	NNP	ORG	4	nmod
    8	,	,			
    9	was	VBD		10	auxpass
    10	bit	NN		0	ROOT
    11	by	IN		13	case
    12	a	DT		13	det
    13	dog	NN		10	nmod
    14	on	IN		15	case
    15	March	DATE-NNP		13	nmod
    16	10th	JJ		15	amod
    17	,	,			
    18	2013	CD		13	amod
    19	.	.			

    1	He	PRP		2	nsubj
    2	died	VBD		0	ROOT
    3	!	.			

    1	John	NNP	PER	3	nmod:poss
    2	's	POS		1	case
    3	daughter	NN		5	dep
    4	Mary	NNP	PER	5	nsubj
    5	expressed	VBD		0	ROOT
    6	sorrow	NN		5	dobj
    7	.	.			

Reading Concrete
~~~~~~~~~~~~~~~~

There are even more annotations stored in this Communication, but for
now we move on to demonstrate handling of the Communication in Python.
The example file contains a single Communication, but many (if
not most) files contain several.  The same code can be used to read
Communications in a regular file, tar archive, or zip
archive::

    from concrete.util import CommunicationReader

    for (comm, filename) in CommunicationReader('serif_dog-bites-man.concrete'):
        print(comm.id)
        print()
        print(comm.text)

This loop prints the unique ID and text (the same text we saw
before) of our one Communication::

    tests/testdata/serif_dog-bites-man.xml

    <DOC id="dog-bites-man" type="other">
    <HEADLINE>
    Dog Bites Man
    </HEADLINE>
    <TEXT>
    <P>
    John Smith, manager of ACMÉ INC, was bit by a dog on March 10th, 2013.
    </P>
    <P>
    He died!
    </P>
    <P>
    John's daughter Mary expressed sorrow.
    </P>
    </TEXT>
    </DOC>

In addition to the general-purpose ``CommunicationReader`` there is a
convenience function for reading a single Communication from a regular
file::

    from concrete.util import read_communication_from_file

    comm = read_communication_from_file('serif_dog-bites-man.concrete')

Communications are broken into *Sections*, which are in turn broken
into *Sentences*, which are in turn broken into *Tokens* (and that's
only scratching the surface).  To traverse this decomposition::

    from concrete.util import lun, get_tokens

    for section in lun(comm.sectionList):
        print('* section')
        for sentence in lun(section.sentenceList):
            print('  + sentence')
            for token in get_tokens(sentence.tokenization):
                print('    - ' + token.text)

The output is::

    * section
    * section
      + sentence
        - John
        - Smith
        - ,
        - manager
        - of
        - ACMÉ
        - INC
        - ,
        - was
        - bit
        - by
        - a
        - dog
        - on
        - March
        - 10th
        - ,
        - 2013
        - .
    * section
      + sentence
        - He
        - died
        - !
    * section
      + sentence
        - John
        - 's
        - daughter
        - Mary
        - expressed
        - sorrow
        - .

Here we used ``get_tokens``, which abstracts the process of extracting
a sequence of *Tokens* from a *Tokenization*, and ``lun``, which
returns its argument or (if its argument is ``None``) an empty list
and stands for "list un-none".  Many fields in Concrete are optional,
including ``Communication.sectionList`` and ``Section.sentenceList``;
checking for ``None`` quickly becomes tedious.

In this Communication the tokens have been annotated with
part-of-speech tags, as we saw previously using
``concrete-inspect.py``.  We can print them with the following code::

    from concrete.util import get_tagged_tokens

    for section in lun(comm.sectionList):
        print('* section')
        for sentence in lun(section.sentenceList):
            print('  + sentence')
            for token_tag in get_tagged_tokens(sentence.tokenization, 'POS'):
                print('    - ' + token_tag.tag)

The output is::

    * section
    * section
      + sentence
        - NNP
        - NNP
        - ,
        - NN
        - IN
        - NNP
        - NNP
        - ,
        - VBD
        - NN
        - IN
        - DT
        - NN
        - IN
        - DATE-NNP
        - JJ
        - ,
        - CD
        - .
    * section
      + sentence
        - PRP
        - VBD
        - .
    * section
      + sentence
        - NNP
        - POS
        - NN
        - NNP
        - VBD
        - NN
        - .

Writing Concrete
~~~~~~~~~~~~~~~~

We can add a new part-of-speech tagging to the Communication as well.
Let's add a simplified version of the current tagging::

    from concrete.util import AnalyticUUIDGeneratorFactory, now_timestamp
    from concrete import TokenTagging, TaggedToken, AnnotationMetadata

    augf = AnalyticUUIDGeneratorFactory(comm)
    aug = augf.create()

    for section in lun(comm.sectionList):
        for sentence in lun(section.sentenceList):
            sentence.tokenization.tokenTaggingList.append(TokenTagging(
                uuid=aug.next(),
                metadata=AnnotationMetadata(
                    tool='Simple POS',
                    timestamp=now_timestamp(),
                    kBest=1
                ),
                taggingType='POS',
                taggedTokenList=[
                    TaggedToken(
                        tokenIndex=original.tokenIndex,
                        tag=original.tag.split('-')[-1][:2],
                    )
                    for original
                    in get_tagged_tokens(sentence.tokenization, 'POS')
                ]
            ))

Here we used ``generate_UUID``, which generates a random *UUID* object,
and ``now_timestamp``, which returns a Concrete timestamp representing
the current time.  But now how do we know which tagging is ours?  Each
annotation's metadata contains a *tool* name, and we can use it to
distinguish between competing annotations::

    from concrete.util import get_tagged_tokens

    for section in lun(comm.sectionList):
        print('* section')
        for sentence in lun(section.sentenceList):
            print('  + sentence')
            token_tag_pairs = zip(
                get_tagged_tokens(sentence.tokenization, 'POS', tool='Serif: part-of-speech'),
                get_tagged_tokens(sentence.tokenization, 'POS', tool='Simple POS')
            )
            for (old_tag, new_tag) in token_tag_pairs:
                print('    - ' + old_tag.tag + ' -> ' + new_tag.tag)

The output shows our new part-of-speech tagging has a smaller, simpler
set of possible values::

    * section
    * section
      + sentence
        - NNP -> NN
        - NNP -> NN
        - , -> ,
        - NN -> NN
        - IN -> IN
        - NNP -> NN
        - NNP -> NN
        - , -> ,
        - VBD -> VB
        - NN -> NN
        - IN -> IN
        - DT -> DT
        - NN -> NN
        - IN -> IN
        - DATE-NNP -> NN
        - JJ -> JJ
        - , -> ,
        - CD -> CD
        - . -> .
    * section
      + sentence
        - PRP -> PR
        - VBD -> VB
        - . -> .
    * section
      + sentence
        - NNP -> NN
        - POS -> PO
        - NN -> NN
        - NNP -> NN
        - VBD -> VB
        - NN -> NN
        - . -> .

Finally, let's write our newly annotated Communication back to disk::

    from concrete.util import CommunicationWriter

    with CommunicationWriter('serif_dog-bites-man.concrete') as writer:
        writer.write(comm)


concrete-inspect.py
-------------------

Use ``concrete-inspect.py`` to quickly explore the contents of a
Communication from the command line.  ``concrete-inspect.py`` and other
scripts are installed to the path along with the concrete-python
library.

--id
~~~~

Run the following command to print the unique ID of our modified
example Communication::

    concrete-inspect.py --id serif_dog-bites-man.concrete

Output::

    tests/testdata/serif_dog-bites-man.xml

--metadata
~~~~~~~~~~

Use ``--metadata`` to print the stored annotations along with their
tool names::

    concrete-inspect.py --metadata serif_dog-bites-man.concrete

Output::

    Communication:  concrete_serif v3.10.1pre

      Tokenization:  Serif: tokens

        Dependency Parse:  Stanford

        Parse:  Serif: parse

        TokenTagging:  Serif: names
        TokenTagging:  Serif: part-of-speech
        TokenTagging:  Simple POS

      EntityMentionSet #0:  Serif: names
      EntityMentionSet #1:  Serif: values
      EntityMentionSet #2:  Serif: mentions

      EntitySet #0:  Serif: doc-entities
      EntitySet #1:  Serif: doc-values

      SituationMentionSet #0:  Serif: relations
      SituationMentionSet #1:  Serif: events

      SituationSet #0:  Serif: relations
      SituationSet #1:  Serif: events

      CommunicationTagging:  lda
      CommunicationTagging:  urgency

--sections
~~~~~~~~~~

Use ``--sections`` to print the text of the Communication, broken out
by section::

    concrete-inspect.py --sections serif_dog-bites-man.concrete

Output::

    Section 0 (0ab68635-c83d-4b02-b8c3-288626968e05), from 81 to 82:



    Section 1 (54902d75-1841-4d8d-b4c5-390d4ef1a47a), from 85 to 162:

    John Smith, manager of ACMÉ INC, was bit by a dog on March 10th, 2013.
    </P>


    Section 2 (7ec8b7d9-6be0-4c62-af57-3c6c48bad711), from 165 to 180:

    He died!
    </P>


    Section 3 (68da91a1-5beb-4129-943d-170c40c7d0f7), from 183 to 228:

    John's daughter Mary expressed sorrow.
    </P>

--entities
~~~~~~~~~~

Use ``--entities`` to print the named entities detected in the
Communication::

    concrete-inspect.py --entities serif_dog-bites-man.concrete

Output::

    Entity Set 0 (Serif: doc-entities):
      Entity 0-0:
          EntityMention 0-0-0:
              tokens:     John Smith
              text:       John Smith
              entityType: PER
              phraseType: PhraseType.NAME
          EntityMention 0-0-1:
              tokens:     John Smith , manager of ACMÉ INC ,
              text:       John Smith, manager of ACMÉ INC,
              entityType: PER
              phraseType: PhraseType.APPOSITIVE
              child EntityMention #0:
                  tokens:     John Smith
                  text:       John Smith
                  entityType: PER
                  phraseType: PhraseType.NAME
              child EntityMention #1:
                  tokens:     manager of ACMÉ INC
                  text:       manager of ACMÉ INC
                  entityType: PER
                  phraseType: PhraseType.COMMON_NOUN
          EntityMention 0-0-2:
              tokens:     manager of ACMÉ INC
              text:       manager of ACMÉ INC
              entityType: PER
              phraseType: PhraseType.COMMON_NOUN
          EntityMention 0-0-3:
              tokens:     He
              text:       He
              entityType: PER
              phraseType: PhraseType.PRONOUN
          EntityMention 0-0-4:
              tokens:     John
              text:       John
              entityType: PER.Individual
              phraseType: PhraseType.NAME

      Entity 0-1:
          EntityMention 0-1-0:
              tokens:     ACMÉ INC
              text:       ACMÉ INC
              entityType: ORG
              phraseType: PhraseType.NAME

      Entity 0-2:
          EntityMention 0-2-0:
              tokens:     John 's daughter Mary
              text:       John's daughter Mary
              entityType: PER.Individual
              phraseType: PhraseType.NAME
              child EntityMention #0:
                  tokens:     Mary
                  text:       Mary
                  entityType: PER
                  phraseType: PhraseType.OTHER
          EntityMention 0-2-1:
              tokens:     daughter
              text:       daughter
              entityType: PER
              phraseType: PhraseType.COMMON_NOUN


    Entity Set 1 (Serif: doc-values):
      Entity 1-0:
          EntityMention 1-0-0:
              tokens:     March 10th , 2013
              text:       March 10th, 2013
              entityType: TIMEX2.TIME
              phraseType: PhraseType.OTHER

--mentions
~~~~~~~~~~

Use ``--mentions`` to show the named entity *mentions* in the
Communication, annotated on the text::

    concrete-inspect.py --mentions serif_dog-bites-man.concrete

Output::

    <ENTITY ID=0><ENTITY ID=0>John Smith</ENTITY> , <ENTITY ID=0>manager of <ENTITY ID=1>ACMÉ INC</ENTITY></ENTITY> ,</ENTITY> was bit by a dog on <ENTITY ID=3>March 10th , 2013</ENTITY> .

    <ENTITY ID=0>He</ENTITY> died !

    <ENTITY ID=2><ENTITY ID=0>John</ENTITY> 's <ENTITY ID=2>daughter</ENTITY> Mary</ENTITY> expressed sorrow .

--situations
~~~~~~~~~~~~

Use ``--situations`` to show the situations detected in the
Communication::

    concrete-inspect.py --situations serif_dog-bites-man.concrete

Output::

    Situation Set 0 (Serif: relations):

    Situation Set 1 (Serif: events):
      Situation 1-0:
          situationType:    Life.Die

--treebank
~~~~~~~~~~

Use ``--treebank`` to show constituency parse trees of the sentences in
the Communication::

    concrete-inspect.py --treebank serif_dog-bites-man.concrete

Output::

    (S (NP (NPP (NNP john)
                (NNP smith))
           (, ,)
           (NP (NPA (NN manager))
               (PP (IN of)
                   (NPP (NNP acme)
                        (NNP inc))))
           (, ,))
       (VP (VBD was)
           (NP (NPA (NN bit))
               (PP (IN by)
                   (NP (NPA (DT a)
                            (NN dog))
                       (PP (IN on)
                           (NP (DATE (DATE-NNP march)
                                     (JJ 10th))
                               (, ,)
                               (NPA (CD 2013))))))))
       (. .))


    (S (NPA (PRP he))
       (VP (VBD died))
       (. !))


    (S (NPA (NPPOS (NPP (NNP john))
                   (POS 's))
            (NN daughter)
            (NPP (NNP mary)))
       (VP (VBD expressed)
           (NPA (NN sorrow)))
       (. .))

Other options
~~~~~~~~~~~~~

Use ``--ner``, ``--pos``, ``--lemmas``, and ``--dependency`` (together
or independently) to show respective token-level information in a
CoNLL-like format, and use ``--text`` to print the text of the
Communication, as described in a previous section.

Run ``concrete-inspect.py --help`` to show a detailed help message
explaining the options discussed above and others.  All
concrete-python scripts have such help messages.


create-comm.py
--------------

Use ``create-comm.py`` to generate a simple Communication from a text
file.  For example, create a file called ``history-of-the-world.txt``
containing the following text::

    The dog ran .
    The cat jumped .

    The dolphin teleported .

Then run the following command to convert it to a Concrete
Communication, creating Sections, Sentences, and Tokens based on
whitespace::

    create-comm.py --annotation-level token history-of-the-world.txt history-of-the-world.concrete

Use ``concrete-inspect.py`` as shown previously to verify the
structure of the Communication::

    concrete-inspect.py --sections history-of-the-world.concrete

Output::

    Section 0 (a188dcdd-1ade-be5d-41c4-fd4d81f71685), from 0 to 30:
    The dog ran .
    The cat jumped .
    
    Section 1 (a188dcdd-1ade-be5d-41c4-fd4d81f7168a), from 32 to 57:
    The dolphin teleported .

Other scripts
-------------

concrete-python provides a number of other scripts, including but not
limited to:

``concrete2json.py``
    reads in a Concrete Communication and prints a
    JSON version of the Communication to stdout.  The JSON is "pretty
    printed" with indentation and whitespace, which makes the JSON
    easier to read and to use for diffs.

``create-comm-tarball.py``
    like ``create-comm.py`` but for multiple files: reads in a tar.gz
    archive of text files, parses them into sections and sentence based
    on whitespace, and writes them back out as Concrete Communications
    in another tar.gz archive.

``fetch-client.py``
    connects to a FetchCommunicationService, retrieves one or more
    Communications (as specified on the command line), and writes them
    to disk.

``fetch-server.py``
    implements FetchCommunicationService, serving Communications to
    clients from a file or directory of Communications on disk.

``search-client.py``
    connects to a SearchService, reading queries from the console and
    printing out results as Communication ids in a loop.

``validate-communication.py``
    reads in a Concrete Communication file and prints out information
    about any invalid fields.  This script is a command-line wrapper
    around the functionality in the ``concrete.validate`` library.

Use the ``--help`` flag for details about the scripts' command line
arguments.


Validating Concrete Communications
----------------------------------

The Python version of the Thrift Libraries does not perform any
validation of Thrift objects.  You should use the
``validate_communication()`` function after reading and before writing
a Concrete Communication::

    from concrete.util import read_communication_from_file
    from concrete.validate import validate_communication

    comm = read_communication_from_file('tests/testdata/serif_dog-bites-man.concrete')

    # Returns True|False, logs details using Python stdlib 'logging' module
    validate_communication(comm)

Thrift fields have three levels of requiredness:

* explicitly labeled as **required**
* explicitly labeled as **optional**
* no requiredness label given ("default required")

Other Concrete tools will raise an exception if a **required** field is
missing on deserialization or serialization, and will raise an
exception if a "default required" field is missing on serialization.
By default, concrete-python does not perform any validation of Thrift
objects on serialization or deserialization.  The Python Thrift classes
do provide shallow ``validate()`` methods, but they only check for
explicitly **required** fields (not "default required" fields) and do
not validate nested objects.

The ``validate_communication()`` function recursively checks a
Communication object for required fields, plus additional checks for
UUID mismatches.





.. _Concrete: http://hltcoe.github.io/concrete/
.. _`online documentation`: http://hltcoe.github.io/concrete-python/
.. _`Apache Thrift`: http://thrift.apache.org
.. _`Concrete GitHub repository`: https://github.com/hltcoe/concrete
.. _serif_dog-bites-man.concrete: https://github.com/hltcoe/concrete-python/raw/master/tests/testdata/serif_dog-bites-man.concrete
.. _CoNLL: http://ufal.mff.cuni.cz/conll2009-st/task-description.html
.. _LICENSE: https://github.com/hltcoe/concrete-python/blob/master/LICENSE
