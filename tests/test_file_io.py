#!/usr/bin/env python

"""
"""

import os
import tarfile
import tempfile
import unittest
import time
import pwd
import grp

from concrete.util.file_io import (
    CommunicationReader,
    CommunicationWriter,
    CommunicationWriterTar,
    CommunicationWriterTGZ,
    read_communication_from_file,
    FileType
)
from concrete.validate import validate_communication

class TestCommunicationReader(unittest.TestCase):
    def test_single_file(self):
        filename = u'tests/testdata/simple_1.concrete'
        reader = CommunicationReader(filename)
        (comm1, comm1_filename) = reader.next()
        self.assertTrue(hasattr(comm1, 'sentenceForUUID'))
        self.assertEqual(u'one', comm1.id)
        self.assertEqual(filename, comm1_filename)

    def test_single_gz_file(self):
        filename = u'tests/testdata/simple_1.concrete.gz'
        reader = CommunicationReader(filename)
        (comm1, comm1_filename) = reader.next()
        self.assertTrue(hasattr(comm1, 'sentenceForUUID'))
        self.assertEqual(u'one', comm1.id)
        self.assertEqual(filename, comm1_filename)

    def test_single_bz2_file(self):
        filename = u'tests/testdata/simple_1.concrete.bz2'
        reader = CommunicationReader(filename)
        (comm1, comm1_filename) = reader.next()
        self.assertTrue(hasattr(comm1, 'sentenceForUUID'))
        self.assertEqual(u'one', comm1.id)
        self.assertEqual(filename, comm1_filename)

    def test_concatenated_file(self):
        filename = u'tests/testdata/simple_concatenated'
        reader = CommunicationReader(filename)
        [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
        for (i, comm_id) in enumerate([u'one', u'two', u'three']):
            self.assertTrue(hasattr(comms[i], 'sentenceForUUID'))
            self.assertEqual(comm_id, comms[i].id)
            self.assertEqual(filename, filenames[i])

    def test_concatenated_gz_file(self):
        filename = u'tests/testdata/simple_concatenated.gz'
        reader = CommunicationReader(filename)
        [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
        for (i, comm_id) in enumerate([u'one', u'two', u'three']):
            self.assertTrue(hasattr(comms[i], 'sentenceForUUID'))
            self.assertEqual(comm_id, comms[i].id)
            self.assertEqual(filename, filenames[i])

    def test_concatenated_bz2_file(self):
        filename = u'tests/testdata/simple_concatenated.bz2'
        reader = CommunicationReader(filename)
        [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
        for (i, comm_id) in enumerate([u'one', u'two', u'three']):
            self.assertTrue(hasattr(comms[i], 'sentenceForUUID'))
            self.assertEqual(comm_id, comms[i].id)
            self.assertEqual(filename, filenames[i])

    def test_tar_file(self):
        filename = u'tests/testdata/simple.tar'
        reader = CommunicationReader(filename)
        [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
        self.assertTrue(hasattr(comms[0], 'sentenceForUUID'))
        self.assertTrue(hasattr(comms[1], 'sentenceForUUID'))
        self.assertTrue(hasattr(comms[2], 'sentenceForUUID'))
        self.assertEqual(u'one', comms[0].id)
        self.assertEqual(u'two', comms[1].id)
        self.assertEqual(u'three', comms[2].id)
        self.assertEqual(u'simple_1.concrete', filenames[0])
        self.assertEqual(u'simple_2.concrete', filenames[1])
        self.assertEqual(u'simple_3.concrete', filenames[2])

    def test_tar_gz_file(self):
        reader = CommunicationReader("tests/testdata/simple.tar.gz")
        [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
        self.assertTrue(hasattr(comms[0], 'sentenceForUUID'))
        self.assertTrue(hasattr(comms[1], 'sentenceForUUID'))
        self.assertTrue(hasattr(comms[2], 'sentenceForUUID'))
        self.assertEqual(u'one', comms[0].id)
        self.assertEqual(u'two', comms[1].id)
        self.assertEqual(u'three', comms[2].id)
        self.assertEqual(u'simple_1.concrete', filenames[0])
        self.assertEqual(u'simple_2.concrete', filenames[1])
        self.assertEqual(u'simple_3.concrete', filenames[2])

    def test_tar_bz2_file(self):
        reader = CommunicationReader("tests/testdata/simple.tar.bz2")
        [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
        self.assertTrue(hasattr(comms[0], 'sentenceForUUID'))
        self.assertTrue(hasattr(comms[1], 'sentenceForUUID'))
        self.assertTrue(hasattr(comms[2], 'sentenceForUUID'))
        self.assertEqual(u'one', comms[0].id)
        self.assertEqual(u'two', comms[1].id)
        self.assertEqual(u'three', comms[2].id)
        self.assertEqual(u'simple_1.concrete', filenames[0])
        self.assertEqual(u'simple_2.concrete', filenames[1])
        self.assertEqual(u'simple_3.concrete', filenames[2])

    def test_nested_tar_file(self):
        reader = CommunicationReader("tests/testdata/simple_nested.tar")
        [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
        self.assertTrue(hasattr(comms[0], 'sentenceForUUID'))
        self.assertTrue(hasattr(comms[1], 'sentenceForUUID'))
        self.assertTrue(hasattr(comms[2], 'sentenceForUUID'))
        self.assertEqual(u'one', comms[0].id)
        self.assertEqual(u'two', comms[1].id)
        self.assertEqual(u'three', comms[2].id)
        self.assertEqual(u'a/b/simple_1.concrete', filenames[0])
        self.assertEqual(u'a/c/simple_2.concrete', filenames[1])
        self.assertEqual(u'a/c/simple_3.concrete', filenames[2])

    def test_zip_file(self):
        reader = CommunicationReader("tests/testdata/simple.zip")
        [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
        self.assertTrue(hasattr(comms[0], 'sentenceForUUID'))
        self.assertTrue(hasattr(comms[1], 'sentenceForUUID'))
        self.assertTrue(hasattr(comms[2], 'sentenceForUUID'))
        self.assertEqual(u'one', comms[0].id)
        self.assertEqual(u'two', comms[1].id)
        self.assertEqual(u'three', comms[2].id)
        self.assertEqual(u'simple_1.concrete', filenames[0])
        self.assertEqual(u'simple_2.concrete', filenames[1])
        self.assertEqual(u'simple_3.concrete', filenames[2])

    def test_explicit_single_file(self):
        filename = u'tests/testdata/simple_1.concrete'
        reader = CommunicationReader(filename, filetype=FileType.STREAM)
        (comm1, comm1_filename) = reader.next()
        self.assertTrue(hasattr(comm1, 'sentenceForUUID'))
        self.assertEqual(u'one', comm1.id)
        self.assertEqual(filename, comm1_filename)

    def test_explicit_single_gz_file(self):
        filename = u'tests/testdata/simple_1.concrete.gz'
        reader = CommunicationReader(filename, filetype=FileType.STREAM_GZ)
        (comm1, comm1_filename) = reader.next()
        self.assertTrue(hasattr(comm1, 'sentenceForUUID'))
        self.assertEqual(u'one', comm1.id)
        self.assertEqual(filename, comm1_filename)

    def test_explicit_single_bz2_file(self):
        filename = u'tests/testdata/simple_1.concrete.bz2'
        reader = CommunicationReader(filename, filetype=FileType.STREAM_BZ2)
        (comm1, comm1_filename) = reader.next()
        self.assertTrue(hasattr(comm1, 'sentenceForUUID'))
        self.assertEqual(u'one', comm1.id)
        self.assertEqual(filename, comm1_filename)

    def test_explicit_concatenated_file(self):
        filename = u'tests/testdata/simple_concatenated'
        reader = CommunicationReader(filename, filetype=FileType.STREAM)
        [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
        for (i, comm_id) in enumerate([u'one', u'two', u'three']):
            self.assertTrue(hasattr(comms[i], 'sentenceForUUID'))
            self.assertEqual(comm_id, comms[i].id)
            self.assertEqual(filename, filenames[i])

    def test_explicit_concatenated_gz_file(self):
        filename = u'tests/testdata/simple_concatenated.gz'
        reader = CommunicationReader(filename, filetype=FileType.STREAM_GZ)
        [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
        for (i, comm_id) in enumerate([u'one', u'two', u'three']):
            self.assertTrue(hasattr(comms[i], 'sentenceForUUID'))
            self.assertEqual(comm_id, comms[i].id)
            self.assertEqual(filename, filenames[i])

    def test_explicit_concatenated_bz2_file(self):
        filename = u'tests/testdata/simple_concatenated.bz2'
        reader = CommunicationReader(filename, filetype=FileType.STREAM_BZ2)
        [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
        for (i, comm_id) in enumerate([u'one', u'two', u'three']):
            self.assertTrue(hasattr(comms[i], 'sentenceForUUID'))
            self.assertEqual(comm_id, comms[i].id)
            self.assertEqual(filename, filenames[i])

    def test_explicit_tar_file(self):
        filename = u'tests/testdata/simple.tar'
        reader = CommunicationReader(filename, filetype=FileType.TAR)
        [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
        self.assertTrue(hasattr(comms[0], 'sentenceForUUID'))
        self.assertTrue(hasattr(comms[1], 'sentenceForUUID'))
        self.assertTrue(hasattr(comms[2], 'sentenceForUUID'))
        self.assertEqual(u'one', comms[0].id)
        self.assertEqual(u'two', comms[1].id)
        self.assertEqual(u'three', comms[2].id)
        self.assertEqual(u'simple_1.concrete', filenames[0])
        self.assertEqual(u'simple_2.concrete', filenames[1])
        self.assertEqual(u'simple_3.concrete', filenames[2])

    def test_explicit_tar_gz_file(self):
        reader = CommunicationReader("tests/testdata/simple.tar.gz",
                                     filetype=FileType.TAR_GZ)
        [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
        self.assertTrue(hasattr(comms[0], 'sentenceForUUID'))
        self.assertTrue(hasattr(comms[1], 'sentenceForUUID'))
        self.assertTrue(hasattr(comms[2], 'sentenceForUUID'))
        self.assertEqual(u'one', comms[0].id)
        self.assertEqual(u'two', comms[1].id)
        self.assertEqual(u'three', comms[2].id)
        self.assertEqual(u'simple_1.concrete', filenames[0])
        self.assertEqual(u'simple_2.concrete', filenames[1])
        self.assertEqual(u'simple_3.concrete', filenames[2])

    def test_explicit_tar_bz2_file(self):
        reader = CommunicationReader("tests/testdata/simple.tar.bz2",
                                     filetype=FileType.TAR_BZ2)
        [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
        self.assertTrue(hasattr(comms[0], 'sentenceForUUID'))
        self.assertTrue(hasattr(comms[1], 'sentenceForUUID'))
        self.assertTrue(hasattr(comms[2], 'sentenceForUUID'))
        self.assertEqual(u'one', comms[0].id)
        self.assertEqual(u'two', comms[1].id)
        self.assertEqual(u'three', comms[2].id)
        self.assertEqual(u'simple_1.concrete', filenames[0])
        self.assertEqual(u'simple_2.concrete', filenames[1])
        self.assertEqual(u'simple_3.concrete', filenames[2])

    def test_explicit_nested_tar_file(self):
        reader = CommunicationReader("tests/testdata/simple_nested.tar",
                                     filetype=FileType.TAR)
        [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
        self.assertTrue(hasattr(comms[0], 'sentenceForUUID'))
        self.assertTrue(hasattr(comms[1], 'sentenceForUUID'))
        self.assertTrue(hasattr(comms[2], 'sentenceForUUID'))
        self.assertEqual(u'one', comms[0].id)
        self.assertEqual(u'two', comms[1].id)
        self.assertEqual(u'three', comms[2].id)
        self.assertEqual(u'a/b/simple_1.concrete', filenames[0])
        self.assertEqual(u'a/c/simple_2.concrete', filenames[1])
        self.assertEqual(u'a/c/simple_3.concrete', filenames[2])

    def test_explicit_zip_file(self):
        reader = CommunicationReader("tests/testdata/simple.zip",
                                     filetype=FileType.ZIP)
        [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
        self.assertTrue(hasattr(comms[0], 'sentenceForUUID'))
        self.assertTrue(hasattr(comms[1], 'sentenceForUUID'))
        self.assertTrue(hasattr(comms[2], 'sentenceForUUID'))
        self.assertEqual(u'one', comms[0].id)
        self.assertEqual(u'two', comms[1].id)
        self.assertEqual(u'three', comms[2].id)
        self.assertEqual(u'simple_1.concrete', filenames[0])
        self.assertEqual(u'simple_2.concrete', filenames[1])
        self.assertEqual(u'simple_3.concrete', filenames[2])

    def test_single_file_no_add_references(self):
        filename = u'tests/testdata/simple_1.concrete'
        reader = CommunicationReader(filename, add_references=False)
        (comm1, comm1_filename) = reader.next()
        self.assertFalse(hasattr(comm1, 'sentenceForUUID'))
        self.assertEqual(u'one', comm1.id)
        self.assertEqual(filename, comm1_filename)

    def test_single_gz_file_no_add_references(self):
        filename = u'tests/testdata/simple_1.concrete.gz'
        reader = CommunicationReader(filename, add_references=False)
        (comm1, comm1_filename) = reader.next()
        self.assertFalse(hasattr(comm1, 'sentenceForUUID'))
        self.assertEqual(u'one', comm1.id)
        self.assertEqual(filename, comm1_filename)

    def test_concatenated_file_no_add_references(self):
        filename = u'tests/testdata/simple_concatenated'
        reader = CommunicationReader(filename, add_references=False)
        [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
        for (i, comm_id) in enumerate([u'one', u'two', u'three']):
            self.assertFalse(hasattr(comms[i], 'sentenceForUUID'))
            self.assertEqual(comm_id, comms[i].id)
            self.assertEqual(filename, filenames[i])

    def test_concatenated_gz_file_no_add_references(self):
        filename = u'tests/testdata/simple_concatenated.gz'
        reader = CommunicationReader(filename, add_references=False)
        [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
        for (i, comm_id) in enumerate([u'one', u'two', u'three']):
            self.assertFalse(hasattr(comms[i], 'sentenceForUUID'))
            self.assertEqual(comm_id, comms[i].id)
            self.assertEqual(filename, filenames[i])

    def test_tar_file_no_add_references(self):
        filename = u'tests/testdata/simple.tar'
        reader = CommunicationReader(filename, add_references=False)
        [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
        self.assertFalse(hasattr(comms[0], 'sentenceForUUID'))
        self.assertFalse(hasattr(comms[1], 'sentenceForUUID'))
        self.assertFalse(hasattr(comms[2], 'sentenceForUUID'))
        self.assertEqual(u'one', comms[0].id)
        self.assertEqual(u'two', comms[1].id)
        self.assertEqual(u'three', comms[2].id)
        self.assertEqual(u'simple_1.concrete', filenames[0])
        self.assertEqual(u'simple_2.concrete', filenames[1])
        self.assertEqual(u'simple_3.concrete', filenames[2])

    def test_tar_gz_file_no_add_references(self):
        reader = CommunicationReader("tests/testdata/simple.tar.gz", add_references=False)
        [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
        self.assertFalse(hasattr(comms[0], 'sentenceForUUID'))
        self.assertFalse(hasattr(comms[1], 'sentenceForUUID'))
        self.assertFalse(hasattr(comms[2], 'sentenceForUUID'))
        self.assertEqual(u'one', comms[0].id)
        self.assertEqual(u'two', comms[1].id)
        self.assertEqual(u'three', comms[2].id)
        self.assertEqual(u'simple_1.concrete', filenames[0])
        self.assertEqual(u'simple_2.concrete', filenames[1])
        self.assertEqual(u'simple_3.concrete', filenames[2])

    def test_zip_file_no_add_references(self):
        reader = CommunicationReader("tests/testdata/simple.zip", add_references=False)
        [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
        self.assertFalse(hasattr(comms[0], 'sentenceForUUID'))
        self.assertFalse(hasattr(comms[1], 'sentenceForUUID'))
        self.assertFalse(hasattr(comms[2], 'sentenceForUUID'))
        self.assertEqual(u'one', comms[0].id)
        self.assertEqual(u'two', comms[1].id)
        self.assertEqual(u'three', comms[2].id)
        self.assertEqual(u'simple_1.concrete', filenames[0])
        self.assertEqual(u'simple_2.concrete', filenames[1])
        self.assertEqual(u'simple_3.concrete', filenames[2])


class TestCommunicationWriter(unittest.TestCase):
    def test_single_file(self):
        comm = read_communication_from_file("tests/testdata/simple_1.concrete")
        writer = CommunicationWriter()
        (file_handle, filename) = tempfile.mkstemp()
        writer.open(filename)
        writer.write(comm)
        writer.close()

        os.remove(filename)

    def test_single_file_ctx_mgr(self):
        comm = read_communication_from_file("tests/testdata/simple_1.concrete")
        (file_handle, filename) = tempfile.mkstemp()
        with CommunicationWriter(filename) as writer:
            writer.write(comm)

        os.remove(filename)


TIME_MARGIN = 60 * 60 * 24


class TestCommunicationWriterTar(unittest.TestCase):
    def test_single_file(self):
        comm = read_communication_from_file("tests/testdata/simple_1.concrete")
        writer = CommunicationWriterTar()
        (file_handle, filename) = tempfile.mkstemp()
        writer.open(filename)
        writer.write(comm, "simple_1.concrete")
        writer.close()

        self.assertTrue(tarfile.is_tarfile(filename))

        f = tarfile.open(filename)

        tarinfo = f.next()
        self.assertIsNotNone(tarinfo)

        self.assertEquals("simple_1.concrete", tarinfo.name)
        self.assertTrue(tarinfo.isreg())
        self.assertTrue(tarinfo.mtime > time.time() - TIME_MARGIN)
        self.assertEquals(os.stat('tests/testdata/simple_1.concrete').st_size, tarinfo.size)
        self.assertEquals(0644, tarinfo.mode)
        self.assertEquals(os.getuid(), tarinfo.uid)
        self.assertEquals(pwd.getpwuid(os.getuid()).pw_name, tarinfo.uname)
        self.assertEquals(os.getgid(), tarinfo.gid)
        self.assertEquals(grp.getgrgid(os.getgid()).gr_name, tarinfo.gname)

        tarinfo = f.next()
        self.assertIsNone(tarinfo)

        f.close()

        os.remove(filename)

    def test_single_file_ctx_mgr(self):
        comm = read_communication_from_file("tests/testdata/simple_1.concrete")
        (file_handle, filename) = tempfile.mkstemp()
        with CommunicationWriterTar(filename) as writer:
            writer.write(comm, "simple_1.concrete")

        self.assertTrue(tarfile.is_tarfile(filename))

        f = tarfile.open(filename)

        tarinfo = f.next()
        self.assertIsNotNone(tarinfo)

        self.assertEquals("simple_1.concrete", tarinfo.name)
        self.assertTrue(tarinfo.isreg())
        self.assertTrue(tarinfo.mtime > time.time() - TIME_MARGIN)
        self.assertEquals(os.stat('tests/testdata/simple_1.concrete').st_size, tarinfo.size)
        self.assertEquals(0644, tarinfo.mode)
        self.assertEquals(os.getuid(), tarinfo.uid)
        self.assertEquals(pwd.getpwuid(os.getuid()).pw_name, tarinfo.uname)
        self.assertEquals(os.getgid(), tarinfo.gid)
        self.assertEquals(grp.getgrgid(os.getgid()).gr_name, tarinfo.gname)

        tarinfo = f.next()
        self.assertIsNone(tarinfo)

        f.close()

        os.remove(filename)

    def test_single_file_default_name(self):
        comm = read_communication_from_file("tests/testdata/simple_1.concrete")
        writer = CommunicationWriterTar()
        (file_handle, filename) = tempfile.mkstemp()
        writer.open(filename)
        writer.write(comm)
        writer.close()

        self.assertTrue(tarfile.is_tarfile(filename))

        f = tarfile.open(filename)

        tarinfo = f.next()
        self.assertIsNotNone(tarinfo)

        self.assertEquals(comm.uuid.uuidString + '.concrete', tarinfo.name)
        self.assertTrue(tarinfo.isreg())
        self.assertTrue(tarinfo.mtime > time.time() - TIME_MARGIN)
        self.assertEquals(os.stat('tests/testdata/simple_1.concrete').st_size, tarinfo.size)
        self.assertEquals(0644, tarinfo.mode)
        self.assertEquals(os.getuid(), tarinfo.uid)
        self.assertEquals(pwd.getpwuid(os.getuid()).pw_name, tarinfo.uname)
        self.assertEquals(os.getgid(), tarinfo.gid)
        self.assertEquals(grp.getgrgid(os.getgid()).gr_name, tarinfo.gname)

        tarinfo = f.next()
        self.assertIsNone(tarinfo)

        f.close()

        os.remove(filename)


class TestCommunicationWriterTGZ(unittest.TestCase):
    def test_single_file(self):
        comm = read_communication_from_file("tests/testdata/simple_1.concrete")
        writer = CommunicationWriterTGZ()
        (file_handle, filename) = tempfile.mkstemp()
        writer.open(filename)
        writer.write(comm, "simple_1.concrete")
        writer.close()

        self.assertTrue(tarfile.is_tarfile(filename))

        f = tarfile.open(filename)

        tarinfo = f.next()
        self.assertIsNotNone(tarinfo)

        self.assertEquals("simple_1.concrete", tarinfo.name)
        self.assertTrue(tarinfo.isreg())
        self.assertTrue(tarinfo.mtime > time.time() - TIME_MARGIN)
        self.assertEquals(os.stat('tests/testdata/simple_1.concrete').st_size, tarinfo.size)
        self.assertEquals(0644, tarinfo.mode)
        self.assertEquals(os.getuid(), tarinfo.uid)
        self.assertEquals(pwd.getpwuid(os.getuid()).pw_name, tarinfo.uname)
        self.assertEquals(os.getgid(), tarinfo.gid)
        self.assertEquals(grp.getgrgid(os.getgid()).gr_name, tarinfo.gname)

        tarinfo = f.next()
        self.assertIsNone(tarinfo)

        f.close()

        os.remove(filename)

    def test_single_file_ctx_mgr(self):
        comm = read_communication_from_file("tests/testdata/simple_1.concrete")
        (file_handle, filename) = tempfile.mkstemp()
        with CommunicationWriterTGZ(filename) as writer:
            writer.write(comm, "simple_1.concrete")

        self.assertTrue(tarfile.is_tarfile(filename))

        f = tarfile.open(filename)

        tarinfo = f.next()
        self.assertIsNotNone(tarinfo)

        self.assertEquals("simple_1.concrete", tarinfo.name)
        self.assertTrue(tarinfo.isreg())
        self.assertTrue(tarinfo.mtime > time.time() - TIME_MARGIN)
        self.assertEquals(os.stat('tests/testdata/simple_1.concrete').st_size, tarinfo.size)
        self.assertEquals(0644, tarinfo.mode)
        self.assertEquals(os.getuid(), tarinfo.uid)
        self.assertEquals(pwd.getpwuid(os.getuid()).pw_name, tarinfo.uname)
        self.assertEquals(os.getgid(), tarinfo.gid)
        self.assertEquals(grp.getgrgid(os.getgid()).gr_name, tarinfo.gname)

        tarinfo = f.next()
        self.assertIsNone(tarinfo)

        f.close()

        os.remove(filename)

    def test_single_file_default_name(self):
        comm = read_communication_from_file("tests/testdata/simple_1.concrete")
        writer = CommunicationWriterTGZ()
        (file_handle, filename) = tempfile.mkstemp()
        writer.open(filename)
        writer.write(comm)
        writer.close()

        self.assertTrue(tarfile.is_tarfile(filename))

        f = tarfile.open(filename)

        tarinfo = f.next()
        self.assertIsNotNone(tarinfo)

        self.assertEquals(comm.uuid.uuidString + '.concrete', tarinfo.name)
        self.assertTrue(tarinfo.isreg())
        self.assertTrue(tarinfo.mtime > time.time() - TIME_MARGIN)
        self.assertEquals(os.stat('tests/testdata/simple_1.concrete').st_size, tarinfo.size)
        self.assertEquals(0644, tarinfo.mode)
        self.assertEquals(os.getuid(), tarinfo.uid)
        self.assertEquals(pwd.getpwuid(os.getuid()).pw_name, tarinfo.uname)
        self.assertEquals(os.getgid(), tarinfo.gid)
        self.assertEquals(grp.getgrgid(os.getgid()).gr_name, tarinfo.gname)

        tarinfo = f.next()
        self.assertIsNone(tarinfo)

        f.close()

        os.remove(filename)


if __name__ == '__main__':
    unittest.main(buffer=True)
