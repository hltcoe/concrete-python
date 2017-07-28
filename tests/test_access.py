from __future__ import unicode_literals
from concrete.util import (
    RedisHashBackedStoreHandler,
    S3BackedStoreHandler,
    prefix_s3_key,
    unprefix_s3_key,
)
from concrete import ServiceInfo

from mock import Mock, sentinel, patch


def test_redis_hash_backed_store_handler_about():
    redis_db = Mock()
    key = Mock()
    handler = RedisHashBackedStoreHandler(redis_db, key)
    assert isinstance(handler.about(), ServiceInfo)


def test_redis_hash_backed_store_handler_alive():
    redis_db = Mock()
    key = Mock()
    handler = RedisHashBackedStoreHandler(redis_db, key)
    assert handler.alive()


@patch('concrete.util.access.RedisCommunicationWriter')
def test_redis_hash_backed_store_handler_store(mock_redis_communication_writer_class):
    mock_redis_communication_writer = mock_redis_communication_writer_class.return_value
    redis_db = Mock()
    key = Mock()

    comm = Mock()
    comm.id = sentinel.comm_id
    handler = RedisHashBackedStoreHandler(redis_db, key)
    mock_redis_communication_writer_class.assert_called_once_with(redis_db, key, key_type='hash')

    handler.store(comm)
    mock_redis_communication_writer.write.assert_called_once_with(comm)


def test_s3_backed_store_handler_about():
    bucket = Mock()
    handler = S3BackedStoreHandler(bucket)
    assert isinstance(handler.about(), ServiceInfo)


def test_s3_backed_store_handler_alive():
    bucket = Mock()
    handler = S3BackedStoreHandler(bucket)
    assert handler.alive()


def test_prefix_s3_key():
    # MD5 of 'asdf' starts with '912e'
    assert prefix_s3_key('asdf', 0) == 'asdf'
    assert prefix_s3_key('asdf', 1) == '9asdf'
    assert prefix_s3_key('asdf', 2) == '91asdf'


def test_unprefix_s3_key():
    assert unprefix_s3_key('xyasdf', 0) == 'xyasdf'
    assert unprefix_s3_key('xyasdf', 1) == 'yasdf'
    assert unprefix_s3_key('xyasdf', 2) == 'asdf'


@patch('concrete.util.access.prefix_s3_key')
@patch('concrete.util.access.write_communication_to_buffer')
def test_s3_backed_store_handler_store(
        mock_write_communication_to_buffer,
        mock_prefix_s3_key):
    key = Mock()
    bucket = Mock(get_key=Mock(side_effect=[key]))

    comm = Mock()
    comm.id = sentinel.comm_id
    handler = S3BackedStoreHandler(bucket, sentinel.prefix_len)

    mock_prefix_s3_key.side_effect = [sentinel.prefixed_key]
    mock_write_communication_to_buffer.side_effect = [sentinel.buf]
    handler.store(comm)
    bucket.get_key.assert_called_once_with(sentinel.prefixed_key, validate=False)
    mock_prefix_s3_key.assert_called_once_with(sentinel.comm_id, sentinel.prefix_len)
    mock_write_communication_to_buffer.assert_called_once_with(comm)
    key.set_contents_from_string.assert_called_once_with(sentinel.buf)
