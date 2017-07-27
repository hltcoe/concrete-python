from __future__ import unicode_literals
from concrete.util import (
    DirectoryBackedCommunicationContainer,
    MemoryBackedCommunicationContainer,
    ZipFileBackedCommunicationContainer,
    RedisHashBackedCommunicationContainer,
    S3BackedCommunicationContainer,
)
from concrete.util import create_comm
from concrete.util import write_communication_to_buffer

from concrete.validate import validate_communication

from pytest import raises, fixture
from mock import Mock, sentinel, patch


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


def test_redis_hash_backed_comm_container_iter():
    redis_db = Mock(hkeys=Mock(side_effect=[[
        sentinel.name0, sentinel.name1, sentinel.name2
    ]]))
    key = sentinel.key
    cc = RedisHashBackedCommunicationContainer(redis_db, key)

    it = iter(cc)
    assert next(it) == sentinel.name0
    assert next(it) == sentinel.name1
    assert next(it) == sentinel.name2
    with raises(StopIteration):
        next(it)
    redis_db.hkeys.assert_called_once_with(key)


def test_redis_hash_backed_comm_container_len():
    redis_db = Mock(hlen=Mock(side_effect=[3]))
    key = sentinel.key
    cc = RedisHashBackedCommunicationContainer(redis_db, key)

    assert 3 == len(cc)
    redis_db.hlen.assert_called_once_with(key)


def test_redis_hash_backed_comm_container_not_contains():
    redis_db = Mock(hexists=Mock(side_effect=[False]))
    key = sentinel.key
    cc = RedisHashBackedCommunicationContainer(redis_db, key)

    assert sentinel.comm_id not in cc
    redis_db.hexists.assert_called_once_with(key, sentinel.comm_id)


def test_redis_hash_backed_comm_container_contains():
    redis_db = Mock(hexists=Mock(side_effect=[True]))
    key = sentinel.key
    cc = RedisHashBackedCommunicationContainer(redis_db, key)

    assert sentinel.comm_id in cc
    redis_db.hexists.assert_called_once_with(key, sentinel.comm_id)


@patch('concrete.util.comm_container.read_communication_from_buffer')
def test_redis_hash_backed_comm_container_not_getitem(
        mock_read_communication_from_buffer):
    redis_db = Mock(hget=Mock(side_effect=[None]))
    key = sentinel.key
    cc = RedisHashBackedCommunicationContainer(redis_db, key)

    with raises(KeyError):
        cc[sentinel.comm_id]
    redis_db.hget.assert_called_once_with(key, sentinel.comm_id)
    assert not mock_read_communication_from_buffer.called


@patch('concrete.util.comm_container.read_communication_from_buffer')
def test_redis_hash_backed_comm_container_getitem(
        mock_read_communication_from_buffer):
    redis_db = Mock(hget=Mock(side_effect=[sentinel.comm_buf]))
    key = sentinel.key
    cc = RedisHashBackedCommunicationContainer(redis_db, key)

    mock_read_communication_from_buffer.side_effect = [sentinel.comm]
    assert cc[sentinel.comm_id] == sentinel.comm
    redis_db.hget.assert_called_once_with(key, sentinel.comm_id)
    mock_read_communication_from_buffer.assert_called_once_with(sentinel.comm_buf)


def test_s3_backed_comm_container_iter():
    keys = [Mock(), Mock(), Mock()]
    keys[0].name = sentinel.name0
    keys[1].name = sentinel.name1
    keys[2].name = sentinel.name2
    bucket = Mock(list=Mock(side_effect=[keys]))
    cc = S3BackedCommunicationContainer(bucket, sentinel.prefix)

    it = iter(cc)
    assert next(it) == sentinel.name0
    assert next(it) == sentinel.name1
    assert next(it) == sentinel.name2
    with raises(StopIteration):
        next(it)
    bucket.list.assert_called_once_with(prefix=sentinel.prefix)


def test_s3_backed_comm_container_len():
    keys = [Mock(), Mock(), Mock()]
    keys[0].name = sentinel.name0
    keys[1].name = sentinel.name1
    keys[2].name = sentinel.name2
    bucket = Mock(list=Mock(side_effect=[keys]))
    cc = S3BackedCommunicationContainer(bucket, sentinel.prefix)

    assert 3 == len(cc)
    bucket.list.assert_called_once_with(prefix=sentinel.prefix)


def test_s3_backed_comm_container_not_contains():
    bucket = Mock(get_key=Mock(side_effect=[None]))
    cc = S3BackedCommunicationContainer(bucket, sentinel.prefix)
    comm_id = Mock(startswith=Mock(return_value=True))

    assert comm_id not in cc
    bucket.get_key.assert_called_once_with(comm_id)
    comm_id.startswith.assert_called_once_with(sentinel.prefix)


def test_s3_backed_comm_container_not_contains_prefix():
    bucket = Mock()
    cc = S3BackedCommunicationContainer(bucket, sentinel.prefix)
    comm_id = Mock(startswith=Mock(return_value=False))

    assert comm_id not in cc
    assert not bucket.get_key.called
    comm_id.startswith.assert_called_once_with(sentinel.prefix)


def test_s3_backed_comm_container_contains():
    bucket = Mock(get_key=Mock(side_effect=[sentinel.key]))
    cc = S3BackedCommunicationContainer(bucket, sentinel.prefix)
    comm_id = Mock(startswith=Mock(return_value=True))

    assert comm_id in cc
    bucket.get_key.assert_called_once_with(comm_id)
    comm_id.startswith.assert_called_once_with(sentinel.prefix)


@patch('concrete.util.comm_container.read_communication_from_buffer')
def test_s3_backed_comm_container_not_getitem(
        mock_read_communication_from_buffer):
    bucket = Mock(get_key=Mock(side_effect=[None]))
    cc = S3BackedCommunicationContainer(bucket, sentinel.prefix)
    comm_id = Mock(startswith=Mock(return_value=True))

    with raises(KeyError):
        cc[comm_id]
    bucket.get_key.assert_called_once_with(comm_id)
    assert not mock_read_communication_from_buffer.called
    comm_id.startswith.assert_called_once_with(sentinel.prefix)


@patch('concrete.util.comm_container.read_communication_from_buffer')
def test_s3_backed_comm_container_not_getitem_prefix(
        mock_read_communication_from_buffer):
    bucket = Mock()
    cc = S3BackedCommunicationContainer(bucket, sentinel.prefix)
    comm_id = Mock(startswith=Mock(return_value=False))

    with raises(KeyError):
        cc[comm_id]
    assert not bucket.get_key.called
    assert not mock_read_communication_from_buffer.called
    comm_id.startswith.assert_called_once_with(sentinel.prefix)


@patch('concrete.util.comm_container.read_communication_from_buffer')
def test_s3_backed_comm_container_getitem(
        mock_read_communication_from_buffer):
    bucket = Mock(get_key=Mock(side_effect=[
        Mock(get_contents_as_string=Mock(side_effect=[sentinel.comm_buf])),
    ]))
    cc = S3BackedCommunicationContainer(bucket, sentinel.prefix)
    comm_id = Mock(startswith=Mock(return_value=True))

    mock_read_communication_from_buffer.side_effect = [sentinel.comm]
    assert cc[comm_id] == sentinel.comm
    bucket.get_key.assert_called_once_with(comm_id)
    mock_read_communication_from_buffer.assert_called_once_with(sentinel.comm_buf)
    comm_id.startswith.assert_called_once_with(sentinel.prefix)
