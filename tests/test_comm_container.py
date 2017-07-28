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
from mock import Mock, sentinel, patch, call


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


@patch('concrete.util.comm_container.unprefix_s3_key')
def test_s3_backed_comm_container_iter(mock_unprefix_s3_key):
    keys = [Mock(), Mock(), Mock()]
    keys[0].name = sentinel.prefixed_name0
    keys[1].name = sentinel.prefixed_name1
    keys[2].name = sentinel.prefixed_name2
    bucket = Mock(list=Mock(side_effect=[keys]))
    mock_unprefix_s3_key.side_effect = [
        sentinel.name0,
        sentinel.name1,
        sentinel.name2,
    ]
    cc = S3BackedCommunicationContainer(bucket, sentinel.prefix_len)

    it = iter(cc)
    assert next(it) == sentinel.name0
    assert next(it) == sentinel.name1
    assert next(it) == sentinel.name2
    with raises(StopIteration):
        next(it)
    bucket.list.assert_called_once_with()
    mock_unprefix_s3_key.assert_has_calls([
        call(sentinel.prefixed_name0, sentinel.prefix_len),
        call(sentinel.prefixed_name1, sentinel.prefix_len),
        call(sentinel.prefixed_name2, sentinel.prefix_len),
    ])


@patch('concrete.util.comm_container.unprefix_s3_key')
def test_s3_backed_comm_container_len(mock_unprefix_s3_key):
    keys = [Mock(), Mock(), Mock()]
    keys[0].name = sentinel.prefixed_name0
    keys[1].name = sentinel.prefixed_name1
    keys[2].name = sentinel.prefixed_name2
    bucket = Mock(list=Mock(side_effect=[keys]))
    cc = S3BackedCommunicationContainer(bucket, sentinel.prefix_len)

    assert 3 == len(cc)
    bucket.list.assert_called_once_with()


@patch('concrete.util.comm_container.prefix_s3_key')
def test_s3_backed_comm_container_not_contains(mock_prefix_s3_key):
    bucket = Mock(get_key=Mock(side_effect=[None]))
    mock_prefix_s3_key.side_effect = [sentinel.prefixed_name]
    cc = S3BackedCommunicationContainer(bucket, sentinel.prefix_len)

    assert sentinel.comm_id not in cc
    bucket.get_key.assert_called_once_with(sentinel.prefixed_name)
    mock_prefix_s3_key.assert_called_once_with(sentinel.comm_id, sentinel.prefix_len)


@patch('concrete.util.comm_container.prefix_s3_key')
def test_s3_backed_comm_container_contains(mock_prefix_s3_key):
    bucket = Mock(get_key=Mock(side_effect=[sentinel.key]))
    mock_prefix_s3_key.side_effect = [sentinel.prefixed_name]
    cc = S3BackedCommunicationContainer(bucket, sentinel.prefix_len)

    assert sentinel.comm_id in cc
    bucket.get_key.assert_called_once_with(sentinel.prefixed_name)
    mock_prefix_s3_key.assert_called_once_with(sentinel.comm_id, sentinel.prefix_len)


@patch('concrete.util.comm_container.prefix_s3_key')
@patch('concrete.util.comm_container.read_communication_from_buffer')
def test_s3_backed_comm_container_not_getitem(
        mock_read_communication_from_buffer, mock_prefix_s3_key):
    bucket = Mock(get_key=Mock(side_effect=[None]))
    mock_prefix_s3_key.side_effect = [sentinel.prefixed_name]
    cc = S3BackedCommunicationContainer(bucket, sentinel.prefix_len)

    with raises(KeyError):
        cc[sentinel.comm_id]
    bucket.get_key.assert_called_once_with(sentinel.prefixed_name)
    mock_prefix_s3_key.assert_called_once_with(sentinel.comm_id, sentinel.prefix_len)
    assert not mock_read_communication_from_buffer.called


@patch('concrete.util.comm_container.prefix_s3_key')
@patch('concrete.util.comm_container.read_communication_from_buffer')
def test_s3_backed_comm_container_getitem(
        mock_read_communication_from_buffer, mock_prefix_s3_key):
    bucket = Mock(get_key=Mock(side_effect=[
        Mock(get_contents_as_string=Mock(side_effect=[sentinel.comm_buf])),
    ]))
    mock_prefix_s3_key.side_effect = [sentinel.prefixed_name]
    mock_read_communication_from_buffer.side_effect = [sentinel.comm]
    cc = S3BackedCommunicationContainer(bucket, sentinel.prefix_len)

    assert cc[sentinel.comm_id] == sentinel.comm
    bucket.get_key.assert_called_once_with(sentinel.prefixed_name)
    mock_prefix_s3_key.assert_called_once_with(sentinel.comm_id, sentinel.prefix_len)
    mock_read_communication_from_buffer.assert_called_once_with(sentinel.comm_buf)
