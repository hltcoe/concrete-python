Copyright 2012-2017 Johns Hopkins University HLTCOE. All rights
reserved.  This software is released under the 2-clause BSD license.
Please see ``LICENSE`` for more information.

Concrete-Python
===============

Concrete-Python is the Python interface to Concrete_, an HLT data
specification defined using Thrift_.

Concrete-Python contains generated Python classes and additional
utilities.  It does not contain the Thrift schema for Concrete, which
can be found in the `Concrete GitHub repository`_.

Requirements
------------

Concrete-Python requires Python 2.7 and the Thrift Python library,
among other Python libraries.  These are installed automatically by
``setup.py`` or ``pip``.  The Thrift compiler is *not* required.

**Note**: The accelerated protocol offers a (de)serialization speedup
of 10x or more; if you would like to use it, ensure a C++ compiler is
available on your system before installing Concrete-Python.
(If a compiler is not available, Concrete-Python will fall back to the
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

Useful Scripts
--------------

The Concrete Python package installs a number of scripts, including:

``concrete-inspect.py``
    reads in a Concrete Communication and prints
    out human-readable information about the Communication's contents
    (such as tokens, POS and NER tags, Entities, Situations, etc) to
    stdout.  This script is a command-line wrapper around the
    functionality in the ``concrete.inspect`` library.
    
``create-comm.py``
    reads in a text file, parses it into sections and sentences based
    on whitespace, and writes it out as a Concrete Communication.
    
``create-comm-tarball.py``
    reads in a tar.gz archive of text files, parses them into sections and
    sentence based on whitespace, and writes them back out as Concrete
    Communications in another tar.gz archive.
    
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

``concrete2json.py``
    reads in a Concrete Communication and prints a
    JSON version of the Communication to stdout.  The JSON is "pretty
    printed" with indentation and whitespace, which makes the JSON
    easier to read and to use for diffs.

``validate-communication.py``
    reads in a Concrete Communication file and prints out information
    about any invalid fields.  This script is a command-line wrapper
    around the functionality in the ``concrete.validate`` library.

Use the ``--help`` flag for details about the scripts' command line
arguments.


Using the code in your project
------------------------------

Concrete types are located under the ``ttypes`` module of their
respective namespace in the schema.  To import and use
``Communication``, for example::

    from concrete import Communication

    foo = Communication()
    foo.text = 'hello world'


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
By default, Concrete-Python does not perform any validation of Thrift
objects on serialization or deserialization.  The Python Thrift classes
do provide shallow ``validate()`` methods, but they only check for
explicitly **required** fields (not "default required" fields) and do
not validate nested objects.

The ``validate_communication()`` function recursively checks a
Communication object for required fields, plus additional checks for
UUID mismatches.


Development
-----------

Please see ``CONTRIBUTING.rst`` for information about contributing to
Concrete-Python.

Contributors to Concrete-Python are listed in ``AUTHORS``.
Please contact us if there is an error in this list.



.. _Concrete: http://hltcoe.github.io
.. _Thrift: http://thrift.apache.org
.. _`Concrete GitHub repository`: https://github.com/hltcoe/concrete
