Copyright 2012-2017 Johns Hopkins University HLTCOE. All rights
reserved.  This software is released under the 2-clause BSD license.
Please see ``LICENSE`` for more information.


concrete-python
===============

concrete-python is the Python interface to Concrete_, an HLT data
specification defined using Thrift_.

concrete-python contains generated Python classes and additional
utilities.  It does not contain the Thrift schema for Concrete, which
can be found in the `Concrete GitHub repository`_.


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

**Note**: here we print the contents of a Communication from Python for
the sake of demonstration, but if that's all you want to do please see
the ``concrete-inspect.py`` command-line script, demonstrated in the
following section.  And note concrete-python provides a number of
scripts for other common tasks!

The example file contains a single Communication, but many (if
not most) files contain several.  The same code can be used to read
Communications in a regular file, tar archive, or zip
archive::

    from concrete.util import CommunicationReader
    for (comm, filename) in CommunicationReader('serif_dog-bites-man.concrete'):
        print(comm.id + ': ' + comm.text)

Of course there is a convenience function for reading a single
Communication from a regular file::

    from concrete.util import read_communication_from_file
    comm = read_communication_from_file('serif_dog-bites-man.concrete')

With the Communication loaded we can start inspecting its contents.
Communications are broken into *Sections*, which are in turn broken
into *Sentences*, which are in turn broken into *Tokens* (and that's
only scratching the surface).  Continuing from where we left off::

    from concrete.util import lun, get_tokens
    for section in lun(comm.sectionList):
        print('* section')
        for sentence in lun(section.sentenceList):
            print('  + sentence')
            for token in get_tokens(sentence.tokenization):
                print('    - ' + token.text)

Here we used ``get_tokens``, which abstracts the process of extracting
a sequence of *Tokens* from a *Tokenization*, and ``lun``, which
returns its argument or (if its argument is ``None``) an empty list
and stands for "list un-none".  Many fields in Concrete are optional,
including ``Communication.sectionList`` and ``Section.sentenceList``;
checking for ``None`` quickly becomes tedious.

In this Communication the tokens have been annotated with
part-of-speech tags::

    from concrete.util import get_tagged_tokens
    for section in lun(comm.sectionList):
        print('* section')
        for sentence in lun(section.sentenceList):
            print('  + sentence')
            for token_tag in get_tagged_tokens(sentence.tokenization, 'POS'):
                print('    - ' + token_tag.tag)

We can add a new part-of-speech tagging to the Communication as well.
Let's add a simplified version of the current tagging::

    from concrete.util import generate_UUID, now_timestamp
    from concrete import TokenTagging, TaggedToken, AnnotationMetadata
    for section in lun(comm.sectionList):
        for sentence in lun(section.sentenceList):
            sentence.tokenization.tokenTaggingList.append(TokenTagging(
                uuid=generate_UUID(),
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

Finally, let's write our newly-annotated Communication back to disk::

    from concrete.util import CommunicationWriter
    with CommunicationWriter('serif_dog-bites-man.concrete') as writer:
        writer.write(comm)


concrete-inspect.py
-------------------

Use ``concrete-inspect.py`` to quickly explore the contents of a
Communication from the command line.  ``concrete-inspect.py`` and other
scripts are installed to the path along with the concrete-python
library.  Run the following commands to explore different parts of our
example Communication::

    concrete-inspect.py --id serif_dog-bites-man.concrete
    concrete-inspect.py --metadata serif_dog-bites-man.concrete
    concrete-inspect.py --sections serif_dog-bites-man.concrete
    concrete-inspect.py --text serif_dog-bites-man.concrete
    concrete-inspect.py --entities serif_dog-bites-man.concrete
    concrete-inspect.py --mentions serif_dog-bites-man.concrete
    concrete-inspect.py --situations serif_dog-bites-man.concrete
    concrete-inspect.py --treebank --ner --pos --lemmas --dependency --char-offsets \
        --pos-tool 'Serif: part-of-speech' serif_dog-bites-man.concrete


create-comm.py
-------------------

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


Development
-----------

Please see ``CONTRIBUTING.rst`` in the source repository for
information about contributing to concrete-python.

Contributors to concrete-python are listed in ``AUTHORS``.
Please contact us if there is an error in this list.



.. _Concrete: http://hltcoe.github.io
.. _Thrift: http://thrift.apache.org
.. _`Concrete GitHub repository`: https://github.com/hltcoe/concrete
.. _serif_dog-bites-man.concrete: https://github.com/hltcoe/concrete-python/raw/master/tests/testdata/serif_dog-bites-man.concrete
