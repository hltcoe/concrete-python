import os
import tarfile
import unittest
import time

from concrete.util.file_io import (
    CommunicationReader,
    CommunicationWriter,
    CommunicationWriterTar,
    CommunicationWriterTGZ,
    read_communication_from_file,
    FileType
)

from pytest import fixture
from tempfile import mkstemp


@fixture
def login_info():
    if os.name == 'nt':
        return dict(
            uid=0,
            gid=0,
            username='',
            groupname='',
        )

    else:
        import pwd
        import grp
        uid = os.getuid()
        gid = os.getgid()
        return dict(
            uid=uid,
            gid=gid,
            username=pwd.getpwuid(uid).pw_name,
            groupname=grp.getgrgid(gid).gr_name,
        )


@fixture
def output_file(request):
    (fd, path) = mkstemp()
    os.close(fd)

    def _remove():
        if os.path.exists(path):
            os.remove(path)

    request.addfinalizer(_remove)
    return path


def test_output_file_finalizer_sanity(output_file):
    assert True


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
        reader = CommunicationReader(
            "tests/testdata/simple.tar.gz", add_references=False)
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
        reader = CommunicationReader(
            "tests/testdata/simple.zip", add_references=False)
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


def test_CommunicationReader_single_file_unicode():
    reader = CommunicationReader(
        "tests/testdata/les-deux-chandeliers.concrete"
    )
    [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
    assert len(comms) == 1
    assert 'tests/testdata/les-deux-chandeliers.txt' == comms[0].id


def test_CommunicationReader_tar_gz_file_unicode():
    reader = CommunicationReader(
        "tests/testdata/les-deux-chandeliers.concrete.tar.gz"
    )
    [comms, filenames] = zip(*[(c, f) for (c, f) in reader])
    assert len(comms) == 2
    assert 'les-deux-chandeliers/l0.txt' == comms[0].id
    assert 'les-deux-chandeliers/l1.txt' == comms[1].id


def test_CommunicationWriter_fixed_point(output_file):
    input_file = 'tests/testdata/simple_1.concrete'
    comm = read_communication_from_file(input_file)

    writer = CommunicationWriter()
    try:
        writer.open(output_file)
        writer.write(comm)
    finally:
        writer.close()

    with open(input_file, 'rb') as expected_f:
        expected_data = expected_f.read()
        with open(output_file, 'rb') as actual_f:
            actual_data = actual_f.read()
            assert expected_data == actual_data


def test_CommunicationWriter_fixed_point_ctx_mgr(output_file):
    input_file = 'tests/testdata/simple_1.concrete'
    comm = read_communication_from_file(input_file)

    with CommunicationWriter(output_file) as writer:
        writer.write(comm)

    with open(input_file, 'rb') as expected_f:
        expected_data = expected_f.read()
        with open(output_file, 'rb') as actual_f:
            actual_data = actual_f.read()
            assert expected_data == actual_data


def test_CommunicationWriter_fixed_point_unicode(output_file):
    input_file = 'tests/testdata/les-deux-chandeliers.concrete'
    comm = read_communication_from_file(input_file)

    with CommunicationWriter(output_file) as writer:
        writer.write(comm)

    with open(input_file, 'rb') as expected_f:
        expected_data = expected_f.read()
        with open(output_file, 'rb') as actual_f:
            actual_data = actual_f.read()
            assert expected_data == actual_data


TIME_MARGIN = 60 * 60 * 24


def test_CommunicationWriterTar_single_file(output_file, login_info):
    comm = read_communication_from_file("tests/testdata/simple_1.concrete")
    writer = CommunicationWriterTar()
    try:
        writer.open(output_file)
        writer.write(comm, "simple_1.concrete")
    finally:
        writer.close()

    assert tarfile.is_tarfile(output_file)

    f = tarfile.open(output_file)

    tarinfo = f.next()
    assert tarinfo is not None

    assert "simple_1.concrete" == tarinfo.name
    assert tarinfo.isreg()
    assert tarinfo.mtime > time.time() - TIME_MARGIN
    assert os.stat('tests/testdata/simple_1.concrete').st_size == tarinfo.size
    assert 0644 == tarinfo.mode
    assert login_info['uid'] == tarinfo.uid
    assert login_info['username'] == tarinfo.uname
    assert login_info['gid'] == tarinfo.gid
    assert login_info['groupname'] == tarinfo.gname

    tarinfo = f.next()
    assert tarinfo is None

    f.close()


def test_CommunicationWriterTar_single_file_ctx_mgr(output_file, login_info):
    comm = read_communication_from_file("tests/testdata/simple_1.concrete")
    with CommunicationWriterTar(output_file) as writer:
        writer.write(comm, "simple_1.concrete")

    assert tarfile.is_tarfile(output_file)

    f = tarfile.open(output_file)

    tarinfo = f.next()
    assert tarinfo is not None

    assert "simple_1.concrete" == tarinfo.name
    assert tarinfo.isreg()
    assert tarinfo.mtime > time.time() - TIME_MARGIN
    assert os.stat('tests/testdata/simple_1.concrete').st_size == tarinfo.size
    assert 0644 == tarinfo.mode
    assert login_info['uid'] == tarinfo.uid
    assert login_info['username'] == tarinfo.uname
    assert login_info['gid'] == tarinfo.gid
    assert login_info['groupname'] == tarinfo.gname

    tarinfo = f.next()
    assert tarinfo is None

    f.close()


def test_CommunicationWriterTar_single_file_fixed_point(output_file,
                                                        login_info):
    comm = read_communication_from_file("tests/testdata/simple_1.concrete")
    with CommunicationWriterTar(output_file) as writer:
        writer.write(comm, "simple_1.concrete")

    assert tarfile.is_tarfile(output_file)

    f = tarfile.open(output_file)

    tarinfo = f.next()
    assert tarinfo is not None

    assert "simple_1.concrete" == tarinfo.name
    actual_data = f.extractfile(tarinfo).read()
    with open('tests/testdata/simple_1.concrete', 'rb') as expected_f:
        expected_data = expected_f.read()
        assert expected_data == actual_data

    tarinfo = f.next()
    assert tarinfo is None

    f.close()


def test_CommunicationWriterTar_single_file_fixed_point_unicode(output_file,
                                                                login_info):
    comm = read_communication_from_file(
        "tests/testdata/les-deux-chandeliers.concrete"
    )
    with CommunicationWriterTar(output_file) as writer:
        writer.write(comm, "les-deux-chandeliers.concrete")

    assert tarfile.is_tarfile(output_file)

    f = tarfile.open(output_file)

    tarinfo = f.next()
    assert tarinfo is not None

    assert "les-deux-chandeliers.concrete" == tarinfo.name
    actual_data = f.extractfile(tarinfo).read()
    with open('tests/testdata/les-deux-chandeliers.concrete',
              'rb') as expected_f:
        expected_data = expected_f.read()
        assert expected_data == actual_data

    tarinfo = f.next()
    assert tarinfo is None

    f.close()


def test_CommunicationWriterTar_single_file_default_name(output_file,
                                                         login_info):
    comm = read_communication_from_file("tests/testdata/simple_1.concrete")
    writer = CommunicationWriterTar()
    try:
        writer.open(output_file)
        writer.write(comm)
    finally:
        writer.close()

    assert tarfile.is_tarfile(output_file)

    f = tarfile.open(output_file)

    tarinfo = f.next()
    assert tarinfo is not None

    assert comm.uuid.uuidString + '.concrete' == tarinfo.name
    assert tarinfo.isreg()
    assert tarinfo.mtime > time.time() - TIME_MARGIN
    assert os.stat('tests/testdata/simple_1.concrete').st_size == tarinfo.size
    assert 0644 == tarinfo.mode
    assert login_info['uid'] == tarinfo.uid
    assert login_info['username'] == tarinfo.uname
    assert login_info['gid'] == tarinfo.gid
    assert login_info['groupname'] == tarinfo.gname

    tarinfo = f.next()
    assert tarinfo is None

    f.close()


def test_CommunicationWriterTGZ_single_file(output_file, login_info):
    comm = read_communication_from_file("tests/testdata/simple_1.concrete")
    writer = CommunicationWriterTGZ()
    try:
        writer.open(output_file)
        writer.write(comm, "simple_1.concrete")
    finally:
        writer.close()

    assert tarfile.is_tarfile(output_file)

    f = tarfile.open(output_file)

    tarinfo = f.next()
    assert tarinfo is not None

    assert "simple_1.concrete" == tarinfo.name
    assert tarinfo.isreg()
    assert tarinfo.mtime > time.time() - TIME_MARGIN
    assert os.stat('tests/testdata/simple_1.concrete').st_size == tarinfo.size
    assert 0644 == tarinfo.mode
    assert login_info['uid'] == tarinfo.uid
    assert login_info['username'] == tarinfo.uname
    assert login_info['gid'] == tarinfo.gid
    assert login_info['groupname'] == tarinfo.gname

    tarinfo = f.next()
    assert tarinfo is None

    f.close()


def test_CommunicationWriterTGZ_single_file_ctx_mgr(output_file, login_info):
    comm = read_communication_from_file("tests/testdata/simple_1.concrete")
    with CommunicationWriterTGZ(output_file) as writer:
        writer.write(comm, "simple_1.concrete")

    assert tarfile.is_tarfile(output_file)

    f = tarfile.open(output_file)

    tarinfo = f.next()
    assert tarinfo is not None

    assert "simple_1.concrete" == tarinfo.name
    assert tarinfo.isreg()
    assert tarinfo.mtime > time.time() - TIME_MARGIN
    assert os.stat('tests/testdata/simple_1.concrete').st_size == tarinfo.size
    assert 0644 == tarinfo.mode
    assert login_info['uid'] == tarinfo.uid
    assert login_info['username'] == tarinfo.uname
    assert login_info['gid'] == tarinfo.gid
    assert login_info['groupname'] == tarinfo.gname

    tarinfo = f.next()
    assert tarinfo is None

    f.close()


def test_CommunicationWriterTGZ_single_file_default_name(output_file,
                                                         login_info):
    comm = read_communication_from_file("tests/testdata/simple_1.concrete")
    writer = CommunicationWriterTGZ()
    try:
        writer.open(output_file)
        writer.write(comm)
    finally:
        writer.close()

    assert tarfile.is_tarfile(output_file)

    f = tarfile.open(output_file)

    tarinfo = f.next()
    assert tarinfo is not None

    assert comm.uuid.uuidString + '.concrete' == tarinfo.name
    assert tarinfo.isreg()
    assert tarinfo.mtime > time.time() - TIME_MARGIN
    assert os.stat('tests/testdata/simple_1.concrete').st_size == tarinfo.size
    assert 0644 == tarinfo.mode
    assert login_info['uid'] == tarinfo.uid
    assert login_info['username'] == tarinfo.uname
    assert login_info['gid'] == tarinfo.gid
    assert login_info['groupname'] == tarinfo.gname

    tarinfo = f.next()
    assert tarinfo is None

    f.close()
