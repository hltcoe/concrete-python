#!/usr/bin/env python

"""
"""

import unittest

from concrete.util.simple_comm import create_simple_comm

class TestSimpleComm(unittest.TestCase):
    def test_generate_uuid(self):
        comm = create_simple_comm('one')
        self.assertEqual('one', comm.id)


if __name__ == '__main__':
    unittest.main(buffer=True)
