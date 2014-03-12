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

Install Concrete using the pip package manager:

    pip install git+https://github.com/charman/concrete-python.git#egg=concrete


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
