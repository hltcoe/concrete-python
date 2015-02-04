#!/usr/bin/env python

"""
"""

import unittest

from concrete.util import CommunicationReader
from concrete.validate import validate_communication

class TestCommunicationReader(unittest.TestCase):
    def test_single_file(self):
        reader = CommunicationReader("tests/testdata/simple_1.concrete")
        comm1 = reader.next()
        self.assertEqual(u'one', comm1.id)

    def test_single_gz_file(self):
        reader = CommunicationReader("tests/testdata/simple_1.concrete.gz")
        comm1 = reader.next()
        self.assertEqual(u'one', comm1.id)

    def test_concatenated_file(self):
        reader = CommunicationReader("tests/testdata/simple_concatenated")
        comms = [c for c in reader]
        self.assertEqual(u'one', comms[0].id)
        self.assertEqual(u'two', comms[1].id)
        self.assertEqual(u'three', comms[2].id)

    def test_concatenated_gz_file(self):
        reader = CommunicationReader("tests/testdata/simple_concatenated.gz")
        comms = [c for c in reader]
        self.assertEqual(u'one', comms[0].id)
        self.assertEqual(u'two', comms[1].id)
        self.assertEqual(u'three', comms[2].id)

    def test_tar_file(self):
        reader = CommunicationReader("tests/testdata/simple.tar")
        comms = [c for c in reader]
        self.assertEqual(u'one', comms[0].id)
        self.assertEqual(u'two', comms[1].id)
        self.assertEqual(u'three', comms[2].id)

    def test_tar_gz_file(self):
        reader = CommunicationReader("tests/testdata/simple.tar.gz")
        comms = [c for c in reader]
        self.assertEqual(u'one', comms[0].id)
        self.assertEqual(u'two', comms[1].id)
        self.assertEqual(u'three', comms[2].id)

    def test_zip_file(self):
        reader = CommunicationReader("tests/testdata/simple.zip")
        comms = [c for c in reader]
        self.assertEqual(u'one', comms[0].id)
        self.assertEqual(u'two', comms[1].id)
        self.assertEqual(u'three', comms[2].id)


if __name__ == '__main__':
    unittest.main(buffer=True)
