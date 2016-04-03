Copyright 2012-2015 Johns Hopkins University HLTCOE. All rights
reserved.  This software is released under the 2-clause BSD license.
See LICENSE.md in the project root directory.

Concrete - Python
=================

Python modules and scripts for working with
[Concrete](https://github.com/hltcoe/concrete), an HLT data
specification defined using [Thrift](http://thrift.apache.org).

This repository contains the Python classes generated by the Thrift
compiler, but not the .thrift definition files that were used to
generate these classes.  The .thrift definition files can be found in
the Concrete GitHub repository: https://github.com/hltcoe/concrete

The `accel` branch of Concrete-Python supports the accelerated thrift
protocols.  For many workloads these are 10 to 30 times faster than the
pure Python protocols.  To take advantage of them, check out the
`accel` branch from the Concrete-Python Git repository and follow the
README there to install.

Requirements
------------

Concrete-Python requires Python 2.7 and a snapshot of the Thrift Python
library with accelerated protocol support.  To install on the COE grid,
from the same directory as this README, do:

```
bash coe-install-fast-thrift.bash
pip install --user .
```

On the CLSP grid, do:

```
bash clsp-install-fast-thrift.bash
pip install --user .
```

On MARCC, do:

```
bash marcc-install-fast-thrift.bash
pip install --user .
```

If you are not on the COE or CLSP grids or MARCC you will need to build
a modern Thrift yourself; see the end of this README for details.
The other libraries are installed automatically by
`setup.py` or `pip`.  Note the Thrift compiler is not required.

**Note on Windows compatibility**: The `thrift` Python package (and
thus the Concrete Python package) does not seem to work with the
[Python Windows binaries from
Python.org](https://www.python.org/downloads/windows/) (32 and 64-bit
versions) on 64-bit Windows.  The `thrift` package does work using the
version of Python that comes with 64-bit Cygwin on 64-bit Windows.

Installation
------------

You can install Concrete using the `pip` package manager:

```
pip install concrete
```

or by cloning the repository and running `setup.py`:

```
git clone https://github.com/hltcoe/concrete-python.git
cd concrete-python
python setup.py test
python setup.py install
```

Useful Scripts
--------------

The Concrete Python package comes with three scripts:

* `concrete_inspect.py` reads in a Concrete Communication and prints
  out human-readable information about the Communication's contents
  (such as tokens, POS and NER tags, Entities, Situations, etc) to
  stdout.

* `concrete2json.py` reads in a Concrete Communication and prints a
  JSON version of the Communication to stdout.  The JSON is "pretty
  printed" with indentation and whitespace, which makes the JSON
  easier to read and to use for diffs.

* `validate_communication.py` reads in a Concrete Communication file
  and prints out information about any invalid fields.  This script is
  a command-line wrapper around the functionality in the
  `concrete.validate` library.

Use the `--help` flag for details about the scripts' command line
arguments.


Using the code in your project
------------------------------

Compiled Python classes end up in the `concrete` namespace. You can
use them by importing them as follows:

```python
from concrete import Communication

foo = Communication()
foo.text = 'hello world'
...
```


Validating Concrete Communications
----------------------------------

The Python version of the Thrift Libraries does not perform any
validation of Thrift objects.  You should use the
`validate_communication()` function after reading and before writing a
Concrete Communication:

```python
from concrete.util import read_communication_from_file
from concrete.validate import validate_communication

comm = read_communication_from_file('tests/testdata/serif_dog-bites-man.concrete')

# Returns True|False, logs details using Python stdlib 'logging' module
validate_communication(comm)
```

Thrift fields have three levels of requiredness:
* explicitly labeled as **required**
* explicitly labeled as **optional**
* no requiredness label given ("default required")

The Java version of the Thrift libraries will raise an exception if a
**required** field is missing on deserialization or serialization, and
will raise an exception if a "default required" field is missing on
serialization.  The Python version of the Thrift Libraries (as of
Thrift 0.9.1) does not perform any validation of Thrift objects on
serialization or deserialization.  The Python Thrift libraries do
provide a `validate()` function, but this function only checks for
explicitly **required** fields, and not "default required" fields.
The Thrift `validate()` function also only performs shallow validation -
nested data structures are not checked for required fields.

The `validate_communication()` function recursively checks a
Communication object for required fields, plus additional checks for
UUID mismatches.


Building from Thrift definitions
================================

To rebuild the `concrete-python` sources from the concrete Thrift
definitions, use `build.bash`.  This script takes the path to the
`thrift` subdirectory of the `concrete` repository as an optional
argument, generates the Python sources from the `.thrift` files
in that subdirectory, and patches to the generated code as necessary.


Building Thrift with accelerated protocol support
=================================================

To build Thrift with support for the Cython binary and compact
protocol extensions, run:

```
bash install-fast-thrift.bash
```

Note this script will download the Thrift source, build it, and install
it (with Python library support only) to your home directory.

If the build fails because of unsatisfied dependencies, consult the
Thrift build instructions in the concrete-c project.
