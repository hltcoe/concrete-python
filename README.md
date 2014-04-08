Copyright 2012-2014 Johns Hopkins University HLTCOE. All rights
reserved.  This software is released under the 2-clause BSD license.
See LICENSE in the project root directory.

Concrete - Python
========

Requirements
------------

Concrete-Python requires the following:
* Python >= 2.7.x
* 'thrift' Python package >= 0.9.1

Installation
------------

You can install Concrete using the pip package manager:

    pip install git+https://github.com/charman/concrete-python.git#egg=concrete

or by cloning this repository and running setup.py:

    git clone https://github.com/charman/concrete-python.git
    cd concrete-python
    python setup.py install


Using the code in your project
------------------------------

Compiled Python classes end up in the `concrete` namespace. You can
use them by importing them as follows:

```python
from concrete.communication import *
from concrete.communication.ttypes import *

foo = Communication()
foo.text = 'hello world'
...
```
