#!/usr/bin/env python

"""Script to create 'simple*' test files containing multiple Communications

These test files are used by the test script:

  tests/test_file_io.py

This script should *only* be re-run if there are major breaking
changes to the Concrete specification that cause the existing sample
Communications files to be rejected by the Concrete validator.  This
script is not intended to be run as part of the standard test suite.

This Python script is secretly a shell script.
"""

import os

from concrete.util import write_communication_to_file
from concrete.util.simple_comm import create_simple_comm

n1 = 'simple_1.concrete'
n2 = 'simple_2.concrete'
n3 = 'simple_3.concrete'

write_communication_to_file(create_simple_comm('one'), n1)
write_communication_to_file(create_simple_comm('two'), n2)
write_communication_to_file(create_simple_comm('three'), n3)

os.system('gzip < %s > %s.gz' % (n1, n1))
os.system('cat %s %s %s > simple_concatenated' % (n1, n2, n3))
os.system('gzip < simple_concatenated > simple_concatenated.gz')
os.system('tar -cvf simple.tar %s %s %s' % (n1, n2, n3))
os.system('gzip < simple.tar > simple.tar.gz')
os.system('zip simple.zip %s %s %s' % (n1, n2, n3))
os.system('mkdir -p a/b a/c')
os.system('cp %s a/b/' % n1)
os.system('cp %s %s a/c/' % (n2, n3))
os.system('tar -cvf simple_nested.tar a')
