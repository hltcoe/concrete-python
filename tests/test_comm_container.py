import unittest

from concrete.util.comm_container import (
    DirectoryBackedCommunicationContainer,
    MemoryBackedCommunicationContainer,
    ZipFileBackedCommunicationContainer,
)

from concrete.validate import validate_communication


class TestDirectoryBackedCommunicationContainer(unittest.TestCase):
    def test_find_files_recursively(self):
        directory_path = u'tests/testdata/a'
        cc = DirectoryBackedCommunicationContainer(directory_path)
        self.assertEqual(3, len(cc))

    def test_retrieve(self):
        directory_path = u'tests/testdata/a'
        cc = DirectoryBackedCommunicationContainer(directory_path)
        self.assertEqual(3, len(cc))
        self.assertTrue(u'simple_1' in cc)
        for comm_id in cc:
            comm = cc[comm_id]
            self.assertTrue(validate_communication(comm))


class TestMemoryBackedCommunicationContainer(unittest.TestCase):
    def test_filesize_check(self):
        comm_path = u'tests/testdata/simple.tar.gz'
        with self.assertRaises(Exception):
            MemoryBackedCommunicationContainer(comm_path, max_file_size=500)

    def test_retrieve(self):
        comm_path = u'tests/testdata/simple.tar.gz'
        cc = MemoryBackedCommunicationContainer(comm_path)
        self.assertEqual(3, len(cc))
        self.assertTrue(u'one' in cc)
        for comm_id in cc:
            comm = cc[comm_id]
            self.assertTrue(validate_communication(comm))


class TestZipFileBackedCommunicationContainer(unittest.TestCase):
    def test_retrieve(self):
        zipfile_path = u'tests/testdata/simple.zip'
        cc = ZipFileBackedCommunicationContainer(zipfile_path)
        self.assertEqual(3, len(cc))
        self.assertTrue(u'simple_1' in cc)
        for comm_id in cc:
            comm = cc[comm_id]
            self.assertTrue(validate_communication(comm))
