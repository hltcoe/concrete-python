#!/usr/bin/env python

"""Test conversion of Communication object to string
"""

import unittest

from test_helper import read_test_comm


class TestRepr(unittest.TestCase):
    def test_repr(self):
        """Verify that Communications can be converted to strings.

        Checks for the issue addressed in this commit:

          commit 0ee3317454543b63dc7a273d92e5720bb9210b03
          Author: Craig Harman <craig@craigharman.net>
          Date:   Tue Dec 16 13:08:44 2014 -0500

            Fixed infinite recursion bug in Tokenization.__repr__()

            The addition of an in-memory "backpointer" from a Tokenization to the
            Tokenization's enclosing Sentence inadvertently broke the
            (Thrift auto-generated) Tokenization.__repr__() function.  Modified the
            function to ignore the backpointer when generating the string
            representation for a Tokenization.
        """
        comm = read_test_comm()
        s = comm.__repr__()


if __name__ == '__main__':
    unittest.main(buffer=True)
