from __future__ import print_function
from __future__ import unicode_literals
import time
from redis import Redis
from multiprocessing import Process

from concrete.util import (
    read_communication_from_redis_key,
    RedisCommunicationReader,
    write_communication_to_redis_key,
    RedisCommunicationWriter
)
from concrete.util import (
    read_communication_from_buffer,
    write_communication_to_buffer
)
from concrete.util import create_comm

from redis_server import RedisServer

from pytest import fixture, raises


@fixture
def comm_buf_pairs(request):
    comm1 = create_comm('comm-1')
    comm2 = create_comm('comm-2')
    comm3 = create_comm('comm-3')
    buf1 = write_communication_to_buffer(comm1)
    buf2 = write_communication_to_buffer(comm2)
    buf3 = write_communication_to_buffer(comm3)
    return ((comm1, buf1), (comm2, buf2), (comm3, buf3))


def _add_comm_to_list(sleep, port, comm_id, key):
    time.sleep(sleep)
    redis_db = Redis(port=port)
    comm = create_comm(comm_id)
    buf = write_communication_to_buffer(comm)
    redis_db.lpush(key, buf)


def test_read_against_file_contents():
    filename = u'tests/testdata/simple_1.concrete'
    key = 'comm'
    with open(filename, 'rb') as f:
        buf = f.read()
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            redis_db.set(key, buf)
            comm = read_communication_from_redis_key(redis_db, key)

        assert hasattr(comm, 'sentenceForUUID')
        assert 'one' == comm.id


def test_read_against_file_contents_no_add_references():
    filename = u'tests/testdata/simple_1.concrete'
    key = 'comm'
    with open(filename, 'rb') as f:
        buf = f.read()
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            redis_db.set(key, buf)
            comm = read_communication_from_redis_key(
                redis_db, key, add_references=False
            )

        assert not hasattr(comm, 'sentenceForUUID')
        assert 'one' == comm.id


def test_write_against_file_contents():
    filename = u'tests/testdata/simple_1.concrete'
    key = 'comm'
    with open(filename, 'rb') as f:
        f_buf = f.read()
        comm = read_communication_from_buffer(f_buf)
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            write_communication_to_redis_key(redis_db, key, comm)
            assert f_buf == redis_db.get(key)


def test_read_write_fixed_point():
    key = 'comm'
    comm = create_comm('comm-1')
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        buf_1 = write_communication_to_redis_key(redis_db, key, comm)
        buf_2 = write_communication_to_redis_key(
            redis_db, key,
            read_communication_from_redis_key(redis_db, key)
        )
        assert buf_1 == buf_2


def test_reader_set(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        redis_db.sadd(key, write_communication_to_buffer(comm1))
        redis_db.sadd(key, write_communication_to_buffer(comm2))
        redis_db.sadd(key, write_communication_to_buffer(comm3))
        reader = RedisCommunicationReader(redis_db, key, key_type='set')
        comms = [c for c in reader]
        ids = [c.id for c in comms]
        # assert no duplicates
        assert 3 == len(ids)
        assert set(['comm-1', 'comm-2', 'comm-3']) == set(ids)
        assert 3 == len(reader)
        assert hasattr(comms[0], 'sentenceForUUID')
        assert hasattr(comms[1], 'sentenceForUUID')
        assert hasattr(comms[2], 'sentenceForUUID')
        batch_ids = [c.id for c in reader.batch(2)]
        # do this weird thing because set(['foo']) != set([u'foo'])
        assert (
            ('comm-1' in batch_ids and 'comm-2' in batch_ids) or
            ('comm-1' in batch_ids and 'comm-3' in batch_ids) or
            ('comm-2' in batch_ids and 'comm-3' in batch_ids)
        )
        # assert data still there
        ids = [c.id for c in reader]
        assert set(['comm-1', 'comm-2', 'comm-3']) == set(ids)
        assert 3 == redis_db.scard(key)


def test_reader_list(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        redis_db.lpush(key, write_communication_to_buffer(comm1))
        redis_db.lpush(key, write_communication_to_buffer(comm2))
        redis_db.lpush(key, write_communication_to_buffer(comm3))
        reader = RedisCommunicationReader(redis_db, key, key_type='list')
        comms = [c for c in reader]
        ids = [c.id for c in comms]
        assert ['comm-1', 'comm-2', 'comm-3'] == ids
        assert 3 == len(reader)
        assert 'comm-2' == reader[1].id
        assert hasattr(comms[0], 'sentenceForUUID')
        assert hasattr(comms[1], 'sentenceForUUID')
        assert hasattr(comms[2], 'sentenceForUUID')
        # assert data still there
        ids = [c.id for c in reader]
        assert ['comm-1', 'comm-2', 'comm-3'] == ids
        assert 3 == redis_db.llen(key)


def test_reader_hash(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        redis_db.hset(key, comm1.uuid.uuidString,
                      write_communication_to_buffer(comm1))
        redis_db.hset(key, comm2.uuid.uuidString,
                      write_communication_to_buffer(comm2))
        redis_db.hset(key, comm3.uuid.uuidString,
                      write_communication_to_buffer(comm3))
        reader = RedisCommunicationReader(redis_db, key, key_type='hash')
        comms = [c for c in reader]
        ids = [c.id for c in comms]
        # assert no duplicates
        assert 3 == len(ids)
        assert set(['comm-1', 'comm-2', 'comm-3']) == set(ids)
        assert 3 == len(reader)
        assert 'comm-2' == reader[comm2.uuid.uuidString].id
        assert hasattr(comms[0], 'sentenceForUUID')
        assert hasattr(comms[1], 'sentenceForUUID')
        assert hasattr(comms[2], 'sentenceForUUID')
        # assert data still there
        ids = [c.id for c in reader]
        assert set(['comm-1', 'comm-2', 'comm-3']) == set(ids)
        assert 3 == redis_db.hlen(key)


def test_reader_list_left_to_right(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        redis_db.lpush(key, write_communication_to_buffer(comm1))
        redis_db.lpush(key, write_communication_to_buffer(comm2))
        redis_db.lpush(key, write_communication_to_buffer(comm3))
        reader = RedisCommunicationReader(redis_db, key, key_type='list',
                                          right_to_left=False)
        comms = [c for c in reader]
        ids = [c.id for c in comms]
        assert ['comm-3', 'comm-2', 'comm-1'] == ids
        assert 3 == len(reader)
        assert 'comm-1' == reader[2].id
        assert hasattr(comms[0], 'sentenceForUUID')
        assert hasattr(comms[1], 'sentenceForUUID')
        assert hasattr(comms[2], 'sentenceForUUID')
        # assert data still there
        ids = [c.id for c in reader]
        assert ['comm-3', 'comm-2', 'comm-1'] == ids
        assert 3 == redis_db.llen(key)


def test_reader_set_implicit(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        redis_db.sadd(key, write_communication_to_buffer(comm1))
        redis_db.sadd(key, write_communication_to_buffer(comm2))
        redis_db.sadd(key, write_communication_to_buffer(comm3))
        reader = RedisCommunicationReader(redis_db, key)
        ids = [c.id for c in reader]
        # assert no duplicates
        assert 3 == len(ids)
        assert set(['comm-1', 'comm-2', 'comm-3']) == set(ids)


def test_reader_list_implicit(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        redis_db.lpush(key, write_communication_to_buffer(comm1))
        redis_db.lpush(key, write_communication_to_buffer(comm2))
        redis_db.lpush(key, write_communication_to_buffer(comm3))
        reader = RedisCommunicationReader(redis_db, key)
        ids = [c.id for c in reader]
        assert ['comm-1', 'comm-2', 'comm-3'] == ids


def test_reader_hash_implicit(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        redis_db.hset(key, comm1.uuid.uuidString,
                      write_communication_to_buffer(comm1))
        redis_db.hset(key, comm2.uuid.uuidString,
                      write_communication_to_buffer(comm2))
        redis_db.hset(key, comm3.uuid.uuidString,
                      write_communication_to_buffer(comm3))
        reader = RedisCommunicationReader(redis_db, key)
        ids = [c.id for c in reader]
        # assert no duplicates
        assert 3 == len(ids)
        assert set(['comm-1', 'comm-2', 'comm-3']) == set(ids)


def test_reader_set_empty(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        reader = RedisCommunicationReader(redis_db, key, key_type='set')
        assert 0 == len(reader)
        redis_db.sadd(key, write_communication_to_buffer(comm1))
        redis_db.sadd(key, write_communication_to_buffer(comm2))
        redis_db.sadd(key, write_communication_to_buffer(comm3))
        ids = [c.id for c in reader]
        # assert no duplicates
        assert 3 == len(ids)
        assert set(['comm-1', 'comm-2', 'comm-3']) == set(ids)
        assert 3 == len(reader)


def test_reader_list_empty(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        reader = RedisCommunicationReader(redis_db, key, key_type='list')
        assert 0 == len(reader)
        redis_db.lpush(key, write_communication_to_buffer(comm1))
        redis_db.lpush(key, write_communication_to_buffer(comm2))
        redis_db.lpush(key, write_communication_to_buffer(comm3))
        ids = [c.id for c in reader]
        assert ['comm-1', 'comm-2', 'comm-3'] == ids
        assert 3 == len(reader)


def test_reader_hash_empty(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        reader = RedisCommunicationReader(redis_db, key, key_type='hash')
        assert 0 == len(reader)
        redis_db.hset(key, comm1.uuid.uuidString,
                      write_communication_to_buffer(comm1))
        redis_db.hset(key, comm2.uuid.uuidString,
                      write_communication_to_buffer(comm2))
        redis_db.hset(key, comm3.uuid.uuidString,
                      write_communication_to_buffer(comm3))
        ids = [c.id for c in reader]
        # assert no duplicates
        assert 3 == len(ids)
        assert set(['comm-1', 'comm-2', 'comm-3']) == set(ids)
        assert 3 == len(reader)


def test_reader_implicit_empty(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        with raises(Exception):
            RedisCommunicationReader(redis_db, key)


def test_reader_set_no_add_references(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        redis_db.sadd(key, write_communication_to_buffer(comm1))
        redis_db.sadd(key, write_communication_to_buffer(comm2))
        redis_db.sadd(key, write_communication_to_buffer(comm3))
        reader = RedisCommunicationReader(redis_db, key, key_type='set',
                                          add_references=False)
        comms = [c for c in reader]
        ids = [c.id for c in comms]
        # assert no duplicates
        assert 3 == len(ids)
        assert set(['comm-1', 'comm-2', 'comm-3']) == set(ids)
        assert not hasattr(comms[0], 'sentenceForUUID')
        assert not hasattr(comms[1], 'sentenceForUUID')
        assert not hasattr(comms[2], 'sentenceForUUID')


def test_reader_list_no_add_references(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        redis_db.lpush(key, write_communication_to_buffer(comm1))
        redis_db.lpush(key, write_communication_to_buffer(comm2))
        redis_db.lpush(key, write_communication_to_buffer(comm3))
        reader = RedisCommunicationReader(redis_db, key, key_type='list',
                                          add_references=False)
        comms = [c for c in reader]
        ids = [c.id for c in comms]
        assert ['comm-1', 'comm-2', 'comm-3'] == ids
        assert not hasattr(comms[0], 'sentenceForUUID')
        assert not hasattr(comms[1], 'sentenceForUUID')
        assert not hasattr(comms[2], 'sentenceForUUID')


def test_reader_hash_no_add_references(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        redis_db.hset(key, comm1.uuid.uuidString,
                      write_communication_to_buffer(comm1))
        redis_db.hset(key, comm2.uuid.uuidString,
                      write_communication_to_buffer(comm2))
        redis_db.hset(key, comm3.uuid.uuidString,
                      write_communication_to_buffer(comm3))
        reader = RedisCommunicationReader(redis_db, key, key_type='hash',
                                          add_references=False)
        comms = [c for c in reader]
        ids = [c.id for c in comms]
        # assert no duplicates
        assert 3 == len(ids)
        assert set(['comm-1', 'comm-2', 'comm-3']) == set(ids)
        assert not hasattr(comms[0], 'sentenceForUUID')
        assert not hasattr(comms[1], 'sentenceForUUID')
        assert not hasattr(comms[2], 'sentenceForUUID')


def test_reader_set_pop(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        redis_db.sadd(key, write_communication_to_buffer(comm1))
        redis_db.sadd(key, write_communication_to_buffer(comm2))
        redis_db.sadd(key, write_communication_to_buffer(comm3))
        reader = RedisCommunicationReader(redis_db, key, key_type='set',
                                          pop=True)
        it = iter(reader)
        ids = []
        ids.append(next(it).id)
        ids.append(next(it).id)
        assert 1 == redis_db.scard(key)
        ids.append(next(it).id)
        # assert no duplicates
        assert 3 == len(ids)
        assert set(['comm-1', 'comm-2', 'comm-3']) == set(ids)
        # assert data is gone
        assert [] == [c.id for c in reader]
        assert not redis_db.exists(key)
        with raises(StopIteration):
            next(it)


def test_reader_list_pop(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        redis_db.lpush(key, write_communication_to_buffer(comm1))
        redis_db.lpush(key, write_communication_to_buffer(comm2))
        redis_db.lpush(key, write_communication_to_buffer(comm3))
        reader = RedisCommunicationReader(redis_db, key, key_type='list',
                                          pop=True)
        it = iter(reader)
        ids = []
        ids.append(next(it).id)
        ids.append(next(it).id)
        assert 1 == redis_db.llen(key)
        ids.append(next(it).id)
        assert ['comm-1', 'comm-2', 'comm-3'] == ids
        # assert data is gone
        assert [] == [c.id for c in reader]
        assert not redis_db.exists(key)
        with raises(StopIteration):
            next(it)


def test_reader_list_pop_left_to_right(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        redis_db.lpush(key, write_communication_to_buffer(comm1))
        redis_db.lpush(key, write_communication_to_buffer(comm2))
        redis_db.lpush(key, write_communication_to_buffer(comm3))
        reader = RedisCommunicationReader(redis_db, key, key_type='list',
                                          pop=True, right_to_left=False)
        it = iter(reader)
        ids = []
        ids.append(next(it).id)
        ids.append(next(it).id)
        assert 1 == redis_db.llen(key)
        ids.append(next(it).id)
        assert ['comm-3', 'comm-2', 'comm-1'] == ids
        # assert data is gone
        assert [] == [c.id for c in reader]
        assert not redis_db.exists(key)
        with raises(StopIteration):
            next(it)


def test_reader_list_block_pop(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        redis_db.lpush(key, write_communication_to_buffer(comm1))
        redis_db.lpush(key, write_communication_to_buffer(comm2))
        redis_db.lpush(key, write_communication_to_buffer(comm3))
        reader = RedisCommunicationReader(redis_db, key, key_type='list',
                                          pop=True, block=True)
        it = iter(reader)
        ids = []
        ids.append(next(it).id)
        ids.append(next(it).id)
        assert 1 == redis_db.llen(key)
        ids.append(next(it).id)
        assert ['comm-1', 'comm-2', 'comm-3'] == ids
        proc = Process(target=_add_comm_to_list,
                       args=(3, server.port, 'comm-4', key))
        proc.start()
        print('Waiting for new comm to be added (3 sec)...')
        assert 'comm-4' == next(iter(reader)).id
        proc.join()


def test_reader_list_block_pop_left_to_right(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        redis_db.lpush(key, write_communication_to_buffer(comm1))
        redis_db.lpush(key, write_communication_to_buffer(comm2))
        redis_db.lpush(key, write_communication_to_buffer(comm3))
        reader = RedisCommunicationReader(redis_db, key, key_type='list',
                                          pop=True, block=True,
                                          right_to_left=False)
        it = iter(reader)
        ids = []
        ids.append(next(it).id)
        ids.append(next(it).id)
        assert 1 == redis_db.llen(key)
        ids.append(next(it).id)
        assert ['comm-3', 'comm-2', 'comm-1'] == ids
        proc = Process(target=_add_comm_to_list,
                       args=(3, server.port, 'comm-4', key))
        proc.start()
        print('Waiting for new comm to be added (3 sec)...')
        assert 'comm-4' == next(iter(reader)).id
        proc.join()


def test_reader_list_block_pop_timeout(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        redis_db.lpush(key, write_communication_to_buffer(comm1))
        redis_db.lpush(key, write_communication_to_buffer(comm2))
        redis_db.lpush(key, write_communication_to_buffer(comm3))
        reader = RedisCommunicationReader(redis_db, key, key_type='list',
                                          pop=True, block=True,
                                          block_timeout=1)
        it = iter(reader)
        ids = []
        ids.append(next(it).id)
        ids.append(next(it).id)
        assert 1 == redis_db.llen(key)
        ids.append(next(it).id)
        assert ['comm-1', 'comm-2', 'comm-3'] == ids
        with raises(StopIteration):
            print('Waiting for timeout (1 sec)...')
            next(it)


def test_writer_set(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        w = RedisCommunicationWriter(redis_db, key, key_type='set')
        w.write(comm1)
        assert 1 == redis_db.scard(key)
        assert buf1 == redis_db.srandmember(key)
        w.write(comm2)
        w.write(comm3)
        assert 3 == redis_db.scard(key)


def test_writer_list(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        w = RedisCommunicationWriter(redis_db, key, key_type='list')
        w.write(comm1)
        assert 1 == redis_db.llen(key)
        assert buf1 == redis_db.lindex(key, 0)
        w.write(comm2)
        w.write(comm3)
        assert 3 == redis_db.llen(key)
        assert buf1 == redis_db.lindex(key, -1)
        assert buf2 == redis_db.lindex(key, -2)
        assert buf3 == redis_db.lindex(key, -3)


def test_writer_hash(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        w = RedisCommunicationWriter(redis_db, key, key_type='hash')
        w.write(comm1)
        assert 1 == redis_db.hlen(key)
        assert buf1 == redis_db.hget(key, comm1.id)
        w.write(comm2)
        w.write(comm3)
        assert 3 == redis_db.hlen(key)
        assert buf1 == redis_db.hget(key, comm1.id)
        assert buf2 == redis_db.hget(key, comm2.id)
        assert buf3 == redis_db.hget(key, comm3.id)


def test_writer_hash_uuid_key(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        w = RedisCommunicationWriter(
            redis_db, key, key_type='hash', uuid_hash_key=True)
        w.write(comm1)
        assert 1 == redis_db.hlen(key)
        assert buf1 == redis_db.hget(key, comm1.uuid.uuidString)
        w.write(comm2)
        w.write(comm3)
        assert 3 == redis_db.hlen(key)
        assert buf1 == redis_db.hget(key, comm1.uuid.uuidString)
        assert buf2 == redis_db.hget(key, comm2.uuid.uuidString)
        assert buf3 == redis_db.hget(key, comm3.uuid.uuidString)


def test_writer_list_left_to_right(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        w = RedisCommunicationWriter(redis_db, key, key_type='list',
                                     right_to_left=False)
        w.write(comm1)
        assert 1 == redis_db.llen(key)
        assert buf1 == redis_db.lindex(key, 0)
        w.write(comm2)
        w.write(comm3)
        assert 3 == redis_db.llen(key)
        assert buf3 == redis_db.lindex(key, -1)
        assert buf2 == redis_db.lindex(key, -2)
        assert buf1 == redis_db.lindex(key, -3)


def test_writer_set_implicit(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        redis_db.sadd(key, buf1)
        w = RedisCommunicationWriter(redis_db, key)
        w.write(comm2)
        w.write(comm3)
        assert 3 == redis_db.scard(key)


def test_writer_list_implicit(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        redis_db.lpush(key, buf1)
        w = RedisCommunicationWriter(redis_db, key)
        w.write(comm2)
        w.write(comm3)
        assert 3 == redis_db.llen(key)
        assert buf1 == redis_db.lindex(key, -1)
        assert buf2 == redis_db.lindex(key, -2)
        assert buf3 == redis_db.lindex(key, -3)


def test_writer_hash_implicit(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        redis_db.hset(key, comm1.id, buf1)
        w = RedisCommunicationWriter(redis_db, key)
        w.write(comm2)
        w.write(comm3)
        assert 3 == redis_db.hlen(key)
        assert buf1 == redis_db.hget(key, comm1.id)
        assert buf2 == redis_db.hget(key, comm2.id)
        assert buf3 == redis_db.hget(key, comm3.id)


def test_writer_implicit_empty(comm_buf_pairs):
    ((comm1, buf1), (comm2, buf2), (comm3, buf3)) = comm_buf_pairs
    key = 'dataset'
    with RedisServer(loglevel='warning') as server:
        redis_db = Redis(port=server.port)
        with raises(Exception):
            RedisCommunicationWriter(redis_db, key)
