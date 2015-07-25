#!/usr/bin/env python

"""
"""

import unittest

from concrete.util import CommunicationReader

from concrete.util.simple_comm import create_simple_comm, SimpleCommTempFile

class TestSimpleComm(unittest.TestCase):
    def test_simple_comm(self):
        comm = create_simple_comm('one')
        self.assertEqual('one', comm.id)


class TestSimpleCommTempFile(unittest.TestCase):
    def test_simple_comm_temp_file(self):
        with SimpleCommTempFile(n=3) as f:
            reader = CommunicationReader(f.path)
            n = 0
            for (orig_comm, comm_path_pair) in zip(f.communications, reader):
                self.assertEqual(orig_comm.id, comm_path_pair[0].id)
                self.assertEqual(f.path, comm_path_pair[1])
                n += 1
            self.assertEqual(3, n)


if __name__ == '__main__':
    unittest.main(buffer=True)
