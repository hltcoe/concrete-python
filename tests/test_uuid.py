#!/usr/bin/env python

"""
"""

import unittest

from concrete import Communication
from concrete.util import generate_UUID
from concrete.validate import validate_communication

class TestUUID(unittest.TestCase):
    def test_generate_uuid(self):
        comm = Communication()
        comm.uuid = generate_UUID()

    def test_minimial_communication_with_uuid(self):
        comm = Communication()
        comm.id = "myID"
        comm.type = "Test Communication"
        comm.uuid = generate_UUID()
        self.assertTrue(validate_communication(comm))


if __name__ == '__main__':
    unittest.main(buffer=True)
