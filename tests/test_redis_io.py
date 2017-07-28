from __future__ import unicode_literals

from itertools import product

from mock import Mock, sentinel, patch, call
from pytest import raises, mark

from concrete.util.redis_io import (
    read_communication_from_redis_key,
    write_communication_to_redis_key,
    RedisCommunicationReader,
    RedisCommunicationWriter,
)


@patch('concrete.util.redis_io.read_communication_from_buffer')
def test_read_communication_from_redis_key(mock_read_communication_from_buffer):
    redis = Mock(get=Mock(side_effect=[sentinel.buf]))
    mock_read_communication_from_buffer.side_effect = [sentinel.comm]
    assert read_communication_from_redis_key(
        redis, sentinel.key, sentinel.add_references) == sentinel.comm
    redis.get.assert_called_once_with(sentinel.key)
    mock_read_communication_from_buffer.assert_called_once_with(
        sentinel.buf, add_references=sentinel.add_references)


@patch('concrete.util.redis_io.read_communication_from_buffer')
def test_read_communication_from_redis_key_empty(mock_read_communication_from_buffer):
    redis = Mock(get=Mock(side_effect=[None]))
    assert read_communication_from_redis_key(
        redis, sentinel.key, sentinel.add_references) is None
    redis.get.assert_called_once_with(sentinel.key)
    assert not mock_read_communication_from_buffer.called


@patch('concrete.util.redis_io.write_communication_to_buffer')
def test_write_communication_to_redis_key(mock_write_communication_to_buffer):
    redis = Mock(set=Mock())
    mock_write_communication_to_buffer.side_effect = [sentinel.buf]
    write_communication_to_redis_key(redis, sentinel.key, sentinel.comm)
    redis.set.assert_called_once_with(sentinel.key, sentinel.buf)
    mock_write_communication_to_buffer.assert_called_once_with(sentinel.comm)


@mark.parametrize(
    'right_to_left,pop,inferred,block',
    list(product((False, True), (False, True), (False, True), (False,))) +
    list(product((False, True), (True,), (False, True), (True,))),
)
@patch('concrete.util.redis_io.read_communication_from_buffer')
def test_redis_communication_reader_list(
        mock_read_communication_from_buffer, right_to_left, pop, inferred, block):
    redis = Mock(
        llen=Mock(return_value=2),
        lindex=Mock(side_effect=[sentinel.buf0, sentinel.buf1]),
        lpop=Mock(side_effect=[sentinel.buf0, sentinel.buf1, None]),
        rpop=Mock(side_effect=[sentinel.buf0, sentinel.buf1, None]),
        blpop=Mock(side_effect=[
            (sentinel.key, sentinel.buf0), (sentinel.key, sentinel.buf1), None]),
        brpop=Mock(side_effect=[
            (sentinel.key, sentinel.buf0), (sentinel.key, sentinel.buf1), None]),
        type=Mock(return_value=b'list'),
    )
    mock_read_communication_from_buffer.side_effect = [
        sentinel.comm0, sentinel.comm1
    ]

    reader = RedisCommunicationReader(
        redis, sentinel.key, key_type=None if inferred else 'list',
        add_references=sentinel.add_references,
        right_to_left=right_to_left, pop=pop, block=block,
        block_timeout=sentinel.block_timeout)

    it = iter(reader)
    assert next(it) == sentinel.comm0
    assert next(it) == sentinel.comm1
    with raises(StopIteration):
        next(it)

    if inferred:
        redis.type.assert_called_once_with(sentinel.key)
    else:
        assert not redis.type.called

    if pop:
        assert not redis.llen.called
        assert not redis.lindex.called
        if block:
            assert not redis.lpop.called
            assert not redis.rpop.called
            getattr(redis, 'brpop' if right_to_left else 'blpop').assert_has_calls([
                call(sentinel.key, timeout=sentinel.block_timeout),
                call(sentinel.key, timeout=sentinel.block_timeout),
                call(sentinel.key, timeout=sentinel.block_timeout),
            ])
            assert not getattr(redis, 'blpop' if right_to_left else 'brpop').called
        else:
            getattr(redis, 'rpop' if right_to_left else 'lpop').assert_has_calls([
                call(sentinel.key),
                call(sentinel.key),
                call(sentinel.key),
            ])
            assert not getattr(redis, 'lpop' if right_to_left else 'rpop').called
            assert not redis.blpop.called
            assert not redis.brpop.called
    else:
        redis.llen.assert_called_with(sentinel.key)
        redis.lindex.assert_has_calls([
            call(sentinel.key, -1 if right_to_left else 0),
            call(sentinel.key, -2 if right_to_left else 1),
        ])
        assert not redis.lpop.called
        assert not redis.rpop.called
        assert not redis.blpop.called
        assert not redis.brpop.called

    mock_read_communication_from_buffer.assert_has_calls([
        call(sentinel.buf0, add_references=sentinel.add_references),
        call(sentinel.buf1, add_references=sentinel.add_references),
    ])


@mark.parametrize(
    'right_to_left,pop,block',
    list(product((False, True), (False, True), (False,))) +
    list(product((False, True), (True,), (True,))),
)
@patch('concrete.util.redis_io.read_communication_from_buffer')
def test_redis_communication_reader_list_empty(
        mock_read_communication_from_buffer, right_to_left, pop, block):
    redis = Mock(
        llen=Mock(return_value=0),
        lindex=Mock(),
        lpop=Mock(side_effect=[None]),
        rpop=Mock(side_effect=[None]),
        blpop=Mock(side_effect=[None]),
        brpop=Mock(side_effect=[None]),
    )

    reader = RedisCommunicationReader(
        redis, sentinel.key, key_type='list',
        add_references=sentinel.add_references,
        right_to_left=right_to_left, pop=pop, block=block,
        block_timeout=sentinel.block_timeout)

    it = iter(reader)
    with raises(StopIteration):
        next(it)

    if pop:
        if block:
            assert not redis.llen.called
            assert not redis.lindex.called
            assert not redis.lpop.called
            assert not redis.rpop.called
            getattr(redis, 'brpop' if right_to_left else 'blpop').assert_called_once_with(
                sentinel.key, timeout=sentinel.block_timeout)
            assert not getattr(redis, 'blpop' if right_to_left else 'brpop').called
        else:
            assert not redis.llen.called
            assert not redis.lindex.called
            getattr(redis, 'rpop' if right_to_left else 'lpop').assert_called_once_with(
                sentinel.key)
            assert not getattr(redis, 'lpop' if right_to_left else 'rpop').called
            assert not redis.blpop.called
            assert not redis.brpop.called
    else:
        redis.llen.assert_called_with(sentinel.key)
        assert not redis.lindex.called
        assert not redis.lpop.called
        assert not redis.rpop.called
        assert not redis.blpop.called
        assert not redis.brpop.called

    assert not mock_read_communication_from_buffer.called


@mark.parametrize(
    'right_to_left,inferred',
    list(product((False, True), (False, True))),
)
@patch('concrete.util.redis_io.read_communication_from_buffer')
def test_redis_communication_reader_set(
        mock_read_communication_from_buffer, right_to_left, inferred):

    def _sadd(_, buf):
        return {
            sentinel.buf0: 1,
            sentinel.buf1: 0,
            sentinel.buf2: 0,
            sentinel.buf3: 1,
            sentinel.buf4: 0,
        }[buf]

    redis = Mock(
        sscan=Mock(side_effect=[
            (7, [sentinel.buf0, sentinel.buf1]),
            (3, [sentinel.buf2]),
            (0, [sentinel.buf3, sentinel.buf4]),
        ]),
        sadd=Mock(side_effect=_sadd),
        scard=Mock(return_value=2),
        expire=Mock(),
        exists=Mock(side_effect=[True, False]),
        type=Mock(return_value=b'set'),
    )
    mock_read_communication_from_buffer.side_effect = [
        sentinel.comm0, sentinel.comm3
    ]

    reader = RedisCommunicationReader(
        redis, 'my-key', key_type=None if inferred else 'set',
        add_references=sentinel.add_references,
        right_to_left=right_to_left)

    it = iter(reader)
    assert next(it) == sentinel.comm0
    assert next(it) == sentinel.comm3
    with raises(StopIteration):
        next(it)

    if inferred:
        redis.type.assert_called_once_with('my-key')
    else:
        assert not redis.type.called

    redis.sscan.assert_has_calls([
        call('my-key', 0),
        call('my-key', 7),
        call('my-key', 3),
    ])

    mock_read_communication_from_buffer.assert_has_calls([
        call(sentinel.buf0, add_references=sentinel.add_references),
        call(sentinel.buf3, add_references=sentinel.add_references),
    ])


@mark.parametrize(
    'right_to_left,inferred',
    list(product((False, True), (False, True))),
)
@patch('concrete.util.redis_io.read_communication_from_buffer')
def test_redis_communication_reader_set_batch(
        mock_read_communication_from_buffer, right_to_left, inferred):
    redis = Mock(
        srandmember=Mock(side_effect=[
            [sentinel.buf0, sentinel.buf1],
        ]),
        type=Mock(return_value=b'set'),
    )
    mock_read_communication_from_buffer.side_effect = [
        sentinel.comm0, sentinel.comm1
    ]

    reader = RedisCommunicationReader(
        redis, sentinel.key, key_type=None if inferred else 'set',
        add_references=sentinel.add_references,
        right_to_left=right_to_left)

    assert reader.batch(sentinel.batch_size) == [sentinel.comm0, sentinel.comm1]

    if inferred:
        redis.type.assert_called_once_with(sentinel.key)
    else:
        assert not redis.type.called

    redis.srandmember.assert_called_once_with(sentinel.key, sentinel.batch_size)

    mock_read_communication_from_buffer.assert_has_calls([
        call(sentinel.buf0, add_references=sentinel.add_references),
        call(sentinel.buf1, add_references=sentinel.add_references),
    ])


@mark.parametrize(
    'right_to_left,inferred',
    list(product((False, True), (False, True))),
)
@patch('concrete.util.redis_io.read_communication_from_buffer')
def test_redis_communication_reader_hash(
        mock_read_communication_from_buffer, right_to_left, inferred):

    def _sadd(_, comm_id):
        return {
            sentinel.comm_id0: 1,
            sentinel.comm_id1: 0,
            sentinel.comm_id2: 0,
            sentinel.comm_id3: 1,
            sentinel.comm_id4: 0,
        }[comm_id]

    redis = Mock(
        hscan=Mock(side_effect=[
            (7, {sentinel.comm_id0: sentinel.buf0, sentinel.comm_id1: sentinel.buf1}),
            (3, {sentinel.comm_id2: sentinel.buf2}),
            (0, {sentinel.comm_id3: sentinel.buf3, sentinel.comm_id4: sentinel.buf4}),
        ]),
        sadd=Mock(side_effect=_sadd),
        hlen=Mock(return_value=2),
        expire=Mock(),
        exists=Mock(side_effect=[True, False]),
        type=Mock(return_value=b'hash'),
    )
    mock_read_communication_from_buffer.side_effect = [
        sentinel.comm0, sentinel.comm3
    ]

    reader = RedisCommunicationReader(
        redis, 'my-key', key_type=None if inferred else 'hash',
        add_references=sentinel.add_references,
        right_to_left=right_to_left)

    it = iter(reader)
    assert next(it) == sentinel.comm0
    assert next(it) == sentinel.comm3
    with raises(StopIteration):
        next(it)

    if inferred:
        redis.type.assert_called_once_with('my-key')
    else:
        assert not redis.type.called

    redis.hscan.assert_has_calls([
        call('my-key', 0),
        call('my-key', 7),
        call('my-key', 3),
    ])

    mock_read_communication_from_buffer.assert_has_calls([
        call(sentinel.buf0, add_references=sentinel.add_references),
        call(sentinel.buf3, add_references=sentinel.add_references),
    ])


@mark.parametrize(
    'right_to_left,inferred',
    list(product((False, True), (False, True))),
)
@patch('concrete.util.redis_io.read_communication_from_buffer')
def test_redis_communication_reader_set_pop(
        mock_read_communication_from_buffer, right_to_left, inferred):
    redis = Mock(
        spop=Mock(side_effect=[sentinel.buf0, sentinel.buf1, None]),
        type=Mock(return_value=b'set'),
    )
    mock_read_communication_from_buffer.side_effect = [
        sentinel.comm0, sentinel.comm1
    ]

    reader = RedisCommunicationReader(
        redis, sentinel.key, key_type=None if inferred else 'set',
        add_references=sentinel.add_references,
        right_to_left=right_to_left, pop=True)

    it = iter(reader)
    assert next(it) == sentinel.comm0
    assert next(it) == sentinel.comm1
    with raises(StopIteration):
        next(it)

    if inferred:
        redis.type.assert_called_once_with(sentinel.key)
    else:
        assert not redis.type.called

    redis.spop.assert_has_calls([
        call(sentinel.key),
        call(sentinel.key),
        call(sentinel.key),
    ])

    mock_read_communication_from_buffer.assert_has_calls([
        call(sentinel.buf0, add_references=sentinel.add_references),
        call(sentinel.buf1, add_references=sentinel.add_references),
    ])


@mark.parametrize(
    'right_to_left',
    [(False,), (True,)]
)
@patch('concrete.util.redis_io.read_communication_from_buffer')
def test_redis_communication_reader_set_pop_empty(
        mock_read_communication_from_buffer, right_to_left):
    redis = Mock(
        spop=Mock(side_effect=[None]),
        type=Mock(return_value=b'set'),
    )

    reader = RedisCommunicationReader(
        redis, sentinel.key, key_type='set',
        add_references=sentinel.add_references,
        right_to_left=right_to_left, pop=True)

    it = iter(reader)
    with raises(StopIteration):
        next(it)

    assert not redis.type.called

    redis.spop.assert_called_once_with(sentinel.key)

    assert not mock_read_communication_from_buffer.called


@mark.parametrize(
    'right_to_left,inferred,key_type,pop,block',
    list(product((False, True), (False, True), ('set', 'list', 'hash'), (False,), (False,))) +
    list(product((False, True), (False, True), ('set', 'list'), (True,), (False,))) +
    list(product((False, True), (False, True), ('list',), (True,), (True,))),
)
def test_redis_communication_reader_len(right_to_left, inferred, key_type, pop, block):
    redis = Mock(
        llen=Mock(side_effect=[3]),
        hlen=Mock(side_effect=[3]),
        scard=Mock(side_effect=[3]),
        type=Mock(return_value=key_type.encode('utf-8')),
    )

    reader = RedisCommunicationReader(
        redis, sentinel.key, key_type=None if inferred else key_type,
        right_to_left=right_to_left, pop=pop, block=block)

    if inferred:
        redis.type.assert_called_once_with(sentinel.key)
    else:
        assert not redis.type.called

    len(reader)

    if key_type == 'set':
        assert redis.scard.called_once_with(sentinel.key)
        assert not redis.llen.called
        assert not redis.hlen.called
    elif key_type == 'list':
        assert not redis.scard.called
        assert redis.llen.called_once_with(sentinel.key)
        assert not redis.hlen.called
    elif key_type == 'hash':
        assert not redis.scard.called
        assert not redis.llen.called
        assert redis.hlen.called_once_with(sentinel.key)
    else:
        raise ValueError('unexpected key type {}'.format(key_type))


def test_redis_communication_reader_failed_infer():
    redis = Mock(
        type=Mock(return_value=b'none'),
    )
    with raises(Exception):
        RedisCommunicationReader(
            redis, sentinel.key,
            add_references=sentinel.add_references)
    redis.type.assert_called_with(sentinel.key)


@mark.parametrize(
    'key_type',
    [('string',), ('zset',)]
)
def test_redis_communication_reader_failed_key_type(key_type):
    with raises(ValueError):
        RedisCommunicationReader(
            sentinel.redis, sentinel.key, key_type=key_type)


@mark.parametrize(
    'right_to_left,inferred,key_type,pop',
    list(product((False, True), (False, True), ('set', 'hash'), (True,))) +
    list(product((False, True), (False, True), ('set', 'hash', 'list'), (False,))),
)
def test_redis_communication_reader_failed_block(right_to_left, inferred, key_type, pop):
    redis = Mock(
        type=Mock(return_value=key_type.encode('utf-8')),
    )

    with raises(ValueError):
        RedisCommunicationReader(
            redis, sentinel.key, key_type=None if inferred else key_type,
            add_references=sentinel.add_references,
            pop=pop, block=True)

    if not inferred:
        assert not redis.type.called


@mark.parametrize(
    'right_to_left,inferred,key_type,pop,block',
    list(product((False, True), (False, True), ('set',), (False, True), (False,))) +
    list(product((False, True), (False, True), ('hash',), (False,), (False,))) +
    list(product((False, True), (False, True), ('list',), (False, True), (False,))) +
    list(product((False, True), (False, True), ('list',), (True,), (True,))),
)
def test_redis_communication_reader_failed_batch(right_to_left, inferred,
                                                 key_type, pop, block):
    redis = Mock(
        type=Mock(return_value=key_type.encode('utf-8')),
    )

    reader = RedisCommunicationReader(
            redis, sentinel.key, key_type=None if inferred else key_type,
            add_references=sentinel.add_references,
            pop=pop, block=block)

    if inferred:
        redis.type.assert_called_once_with(sentinel.key)
    else:
        assert not redis.type.called

    with raises(Exception):
        reader.batch(sentinel.batch_size)


@mark.parametrize(
    'right_to_left,inferred,block',
    list(product((False, True), (False, True), (False, True))),
)
def test_redis_communication_reader_failed_pop(right_to_left, inferred, block):
    redis = Mock(
        type=Mock(return_value=b'hash'),
    )

    with raises(ValueError):
        RedisCommunicationReader(
            redis, sentinel.key, key_type=None if inferred else 'hash',
            add_references=sentinel.add_references,
            block=block, pop=True)

    if not inferred:
        assert not redis.type.called


@mark.parametrize(
    'right_to_left,inferred',
    list(product((False, True), (False, True))),
)
@patch('concrete.util.redis_io.write_communication_to_buffer')
def test_redis_communication_writer_list(
        mock_write_communication_to_buffer, right_to_left, inferred):
    redis = Mock(
        lpush=Mock(side_effect=[3]),
        rpush=Mock(side_effect=[3]),
        type=Mock(return_value=b'list'),
    )
    mock_write_communication_to_buffer.side_effect = [sentinel.buf]

    writer = RedisCommunicationWriter(
        redis, sentinel.key, key_type=None if inferred else 'list',
        right_to_left=right_to_left)

    if inferred:
        redis.type.assert_called_once_with(sentinel.key)
    else:
        assert not redis.type.called

    writer.write(sentinel.comm)

    getattr(redis, 'lpush' if right_to_left else 'rpush').assert_called_once_with(
        sentinel.key, sentinel.buf)
    assert not getattr(redis, 'rpush' if right_to_left else 'lpush').called

    mock_write_communication_to_buffer.assert_called_once_with(sentinel.comm)


@mark.parametrize(
    'right_to_left,inferred',
    list(product((False, True), (False, True))),
)
@patch('concrete.util.redis_io.write_communication_to_buffer')
def test_redis_communication_writer_set(
        mock_write_communication_to_buffer, right_to_left, inferred):
    redis = Mock(
        sadd=Mock(side_effect=[0]),
        type=Mock(return_value=b'set'),
    )
    mock_write_communication_to_buffer.side_effect = [sentinel.buf]

    writer = RedisCommunicationWriter(
        redis, sentinel.key, key_type=None if inferred else 'set',
        right_to_left=right_to_left)

    if inferred:
        redis.type.assert_called_once_with(sentinel.key)
    else:
        assert not redis.type.called

    writer.write(sentinel.comm)

    redis.sadd.assert_called_once_with(sentinel.key, sentinel.buf)
    assert not getattr(redis, 'rpush' if right_to_left else 'lpush').called

    mock_write_communication_to_buffer.assert_called_once_with(sentinel.comm)


@mark.parametrize(
    'right_to_left,inferred,uuid_hash_key',
    list(product((False, True), (False, True), (False, True))),
)
@patch('concrete.util.redis_io.write_communication_to_buffer')
def test_redis_communication_writer_hash(
        mock_write_communication_to_buffer, right_to_left, inferred,
        uuid_hash_key):
    redis = Mock(
        hset=Mock(side_effect=[0]),
        type=Mock(return_value=b'hash'),
    )
    comm = Mock(id=sentinel.comm_id, uuid=Mock(uuidString=sentinel.comm_uuid))
    mock_write_communication_to_buffer.side_effect = [sentinel.buf]

    writer = RedisCommunicationWriter(
        redis, sentinel.key, key_type=None if inferred else 'hash',
        right_to_left=right_to_left, uuid_hash_key=uuid_hash_key)

    if inferred:
        redis.type.assert_called_once_with(sentinel.key)
    else:
        assert not redis.type.called

    writer.write(comm)

    redis.hset.assert_called_once_with(
        sentinel.key,
        sentinel.comm_uuid if uuid_hash_key else sentinel.comm_id,
        sentinel.buf)
    assert not getattr(redis, 'rpush' if right_to_left else 'lpush').called

    mock_write_communication_to_buffer.assert_called_once_with(comm)


@mark.parametrize(
    'right_to_left,inferred,key_type',
    list(product((False, True), (False, True), ('set', 'list', 'hash'))),
)
def test_redis_communication_writer_clear(right_to_left, inferred, key_type):
    redis = Mock(
        delete=Mock(side_effect=[0]),
        type=Mock(return_value=key_type.encode('utf-8')),
    )

    writer = RedisCommunicationWriter(
        redis, sentinel.key, key_type=None if inferred else 'hash',
        right_to_left=right_to_left)

    if inferred:
        redis.type.assert_called_once_with(sentinel.key)
    else:
        assert not redis.type.called

    writer.clear()

    redis.delete.assert_called_once_with(sentinel.key)


def test_redis_communication_writer_failed_infer():
    redis = Mock(
        type=Mock(return_value=b'none'),
    )
    with raises(Exception):
        RedisCommunicationWriter(
            redis, sentinel.key)
    redis.type.assert_called_with(sentinel.key)


@mark.parametrize(
    'key_type',
    [('string',), ('zset',)]
)
def test_redis_communication_writer_failed_key_type(key_type):
    with raises(ValueError):
        RedisCommunicationWriter(
            sentinel.redis, sentinel.key, key_type=key_type)
