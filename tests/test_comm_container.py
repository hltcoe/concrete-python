from __future__ import unicode_literals
from concrete.util import (
    DirectoryBackedCommunicationContainer,
    MemoryBackedCommunicationContainer,
    ZipFileBackedCommunicationContainer,
    RedisHashBackedCommunicationContainer,
)
from concrete.util import create_comm
from concrete.util import write_communication_to_buffer

from concrete.validate import validate_communication

from pytest import raises, fixture
import mock


@fixture
def comm_id_and_buf(request):
    comm_id = 'temp comm'
    return (comm_id, write_communication_to_buffer(create_comm(comm_id)))


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


def test_memory_backed_comm_container_file_too_large():
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


def test_redis_hash_backed_comm_container_len(comm_id_and_buf):
    redis_db = mock.Mock()
    key = mock.sentinel
    (comm_id, comm_buf) = comm_id_and_buf
    cc = RedisHashBackedCommunicationContainer(redis_db, key)

    redis_db.hlen.side_effect = [3]
    assert 3 == len(cc)
    redis_db.hlen.assert_called_once_with(key)


def test_redis_hash_backed_comm_container_contains(comm_id_and_buf):
    redis_db = mock.Mock()
    key = mock.sentinel
    (comm_id, comm_buf) = comm_id_and_buf
    cc = RedisHashBackedCommunicationContainer(redis_db, key)

    redis_db.hexists.side_effect = [False]
    assert comm_id + 'x' not in cc
    redis_db.hexists.assert_called_once_with(key, comm_id + 'x')


def test_redis_hash_backed_comm_container_not_contains(comm_id_and_buf):
    redis_db = mock.Mock()
    key = mock.sentinel
    (comm_id, comm_buf) = comm_id_and_buf
    cc = RedisHashBackedCommunicationContainer(redis_db, key)

    redis_db.hexists.side_effect = [True]
    assert comm_id in cc
    redis_db.hexists.assert_called_once_with(key, comm_id)


def test_redis_hash_backed_comm_container_not_getitem(comm_id_and_buf):
    redis_db = mock.Mock()
    key = mock.sentinel
    (comm_id, comm_buf) = comm_id_and_buf
    cc = RedisHashBackedCommunicationContainer(redis_db, key)

    redis_db.hget.side_effect = [None]
    with raises(KeyError):
        cc[comm_id + 'x']
    redis_db.hget.assert_called_once_with(key, comm_id + 'x')
