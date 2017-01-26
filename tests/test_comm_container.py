from concrete.util.comm_container import (
    DirectoryBackedCommunicationContainer,
    MemoryBackedCommunicationContainer,
    ZipFileBackedCommunicationContainer,
)

from concrete.validate import validate_communication

from pytest import raises


def test_directory_backed_comm_container_find_files_recursively():
    directory_path = u'tests/testdata/a'
    cc = DirectoryBackedCommunicationContainer(directory_path)
    assert 3 == len(cc)


def test_directory_backed_comm_container_retrieve():
    directory_path = u'tests/testdata/a'
    cc = DirectoryBackedCommunicationContainer(directory_path)
    assert 3 == len(cc)
    assert u'simple_1' in cc
    for comm_id in cc:
        comm = cc[comm_id]
        assert validate_communication(comm)


def test_memory_backed_comm_container_filesize_check():
    comm_path = u'tests/testdata/simple.tar.gz'
    with raises(Exception):
        MemoryBackedCommunicationContainer(comm_path, max_file_size=500)


def test_memory_backed_comm_container_retrieve():
    comm_path = u'tests/testdata/simple.tar.gz'
    cc = MemoryBackedCommunicationContainer(comm_path)
    assert 3 == len(cc)
    assert u'one' in cc
    for comm_id in cc:
        comm = cc[comm_id]
        assert validate_communication(comm)


def test_zip_file_backed_comm_container_retrieve():
    zipfile_path = u'tests/testdata/simple.zip'
    cc = ZipFileBackedCommunicationContainer(zipfile_path)
    assert 3 == len(cc)
    assert u'simple_1' in cc
    for comm_id in cc:
        comm = cc[comm_id]
        assert validate_communication(comm)
