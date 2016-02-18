import unittest

import time
from redis import Redis
from multiprocessing import Process

from concrete.util.redis_io import (
    read_communication_from_redis_key,
    RedisCommunicationReader,
    write_communication_to_redis_key,
    RedisCommunicationWriter
)
from concrete.util.mem_io import (
    read_communication_from_buffer,
    write_communication_to_buffer
)
from concrete.util.simple_comm import create_comm
from redis_server import RedisServer


def _add_comm_to_list(sleep, port, comm_id, key):
    time.sleep(sleep)
    redis_db = Redis(port=port)
    comm = create_comm(comm_id)
    buf = write_communication_to_buffer(comm)
    redis_db.lpush(key, buf)


class TestReadCommunicationFromRedisKey(unittest.TestCase):

    def test_read_against_file_contents(self):
        filename = u'tests/testdata/simple_1.concrete'
        key = 'comm'
        with open(filename, 'rb') as f:
            buf = f.read()
            with RedisServer(loglevel='warning') as server:
                redis_db = Redis(port=server.port)
                redis_db.set(key, buf)
                comm = read_communication_from_redis_key(redis_db, key)

            self.assertTrue(hasattr(comm, 'sentenceForUUID'))
            self.assertEquals('one', comm.id)

    def test_read_against_file_contents_no_add_references(self):
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

            self.assertFalse(hasattr(comm, 'sentenceForUUID'))
            self.assertEquals('one', comm.id)


class TestWriteCommunicationToRedisKey(unittest.TestCase):

    def test_write_against_file_contents(self):
        filename = u'tests/testdata/simple_1.concrete'
        key = 'comm'
        with open(filename, 'rb') as f:
            f_buf = f.read()
            comm = read_communication_from_buffer(f_buf)
            with RedisServer(loglevel='warning') as server:
                redis_db = Redis(port=server.port)
                write_communication_to_redis_key(redis_db, key, comm)
                self.assertEquals(f_buf, redis_db.get(key))

    def test_read_write_fixed_point(self):
        key = 'comm'
        comm = create_comm('comm-1')
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            buf_1 = write_communication_to_redis_key(redis_db, key, comm)
            buf_2 = write_communication_to_redis_key(
                redis_db, key,
                read_communication_from_redis_key(redis_db, key)
            )
            self.assertEquals(buf_1, buf_2)


class TestRedisCommunicationReader(unittest.TestCase):

    def setUp(self):
        self.comm1 = create_comm('comm-1')
        self.comm2 = create_comm('comm-2')
        self.comm3 = create_comm('comm-3')

    def test_set(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            redis_db.sadd(key, write_communication_to_buffer(self.comm1))
            redis_db.sadd(key, write_communication_to_buffer(self.comm2))
            redis_db.sadd(key, write_communication_to_buffer(self.comm3))
            reader = RedisCommunicationReader(redis_db, key, key_type='set')
            comms = [c for c in reader]
            ids = [c.id for c in comms]
            # assert no duplicates
            self.assertEquals(3, len(ids))
            self.assertEquals(set(['comm-1', 'comm-2', 'comm-3']), set(ids))
            self.assertEquals(3, len(reader))
            self.assertTrue(hasattr(comms[0], 'sentenceForUUID'))
            self.assertTrue(hasattr(comms[1], 'sentenceForUUID'))
            self.assertTrue(hasattr(comms[2], 'sentenceForUUID'))
            batch_ids = [c.id for c in reader.batch(2)]
            # do this weird thing because set(['foo']) != set([u'foo'])
            self.assertTrue(
                ('comm-1' in batch_ids and 'comm-2' in batch_ids) or
                ('comm-1' in batch_ids and 'comm-3' in batch_ids) or
                ('comm-2' in batch_ids and 'comm-3' in batch_ids)
            )
            # assert data still there
            ids = [c.id for c in reader]
            self.assertEquals(set(['comm-1', 'comm-2', 'comm-3']), set(ids))
            self.assertEquals(3, redis_db.scard(key))

    def test_list(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            redis_db.lpush(key, write_communication_to_buffer(self.comm1))
            redis_db.lpush(key, write_communication_to_buffer(self.comm2))
            redis_db.lpush(key, write_communication_to_buffer(self.comm3))
            reader = RedisCommunicationReader(redis_db, key, key_type='list')
            comms = [c for c in reader]
            ids = [c.id for c in comms]
            self.assertEquals(['comm-1', 'comm-2', 'comm-3'], ids)
            self.assertEquals(3, len(reader))
            self.assertEquals('comm-2', reader[1].id)
            self.assertTrue(hasattr(comms[0], 'sentenceForUUID'))
            self.assertTrue(hasattr(comms[1], 'sentenceForUUID'))
            self.assertTrue(hasattr(comms[2], 'sentenceForUUID'))
            # assert data still there
            ids = [c.id for c in reader]
            self.assertEquals(['comm-1', 'comm-2', 'comm-3'], ids)
            self.assertEquals(3, redis_db.llen(key))

    def test_hash(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            redis_db.hset(key, self.comm1.uuid.uuidString,
                          write_communication_to_buffer(self.comm1))
            redis_db.hset(key, self.comm2.uuid.uuidString,
                          write_communication_to_buffer(self.comm2))
            redis_db.hset(key, self.comm3.uuid.uuidString,
                          write_communication_to_buffer(self.comm3))
            reader = RedisCommunicationReader(redis_db, key, key_type='hash')
            comms = [c for c in reader]
            ids = [c.id for c in comms]
            # assert no duplicates
            self.assertEquals(3, len(ids))
            self.assertEquals(set(['comm-1', 'comm-2', 'comm-3']), set(ids))
            self.assertEquals(3, len(reader))
            self.assertEquals('comm-2', reader[self.comm2.uuid.uuidString].id)
            self.assertTrue(hasattr(comms[0], 'sentenceForUUID'))
            self.assertTrue(hasattr(comms[1], 'sentenceForUUID'))
            self.assertTrue(hasattr(comms[2], 'sentenceForUUID'))
            # assert data still there
            ids = [c.id for c in reader]
            self.assertEquals(set(['comm-1', 'comm-2', 'comm-3']), set(ids))
            self.assertEquals(3, redis_db.hlen(key))

    def test_list_left_to_right(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            redis_db.lpush(key, write_communication_to_buffer(self.comm1))
            redis_db.lpush(key, write_communication_to_buffer(self.comm2))
            redis_db.lpush(key, write_communication_to_buffer(self.comm3))
            reader = RedisCommunicationReader(redis_db, key, key_type='list',
                                              right_to_left=False)
            comms = [c for c in reader]
            ids = [c.id for c in comms]
            self.assertEquals(['comm-3', 'comm-2', 'comm-1'], ids)
            self.assertEquals(3, len(reader))
            self.assertEquals('comm-1', reader[2].id)
            self.assertTrue(hasattr(comms[0], 'sentenceForUUID'))
            self.assertTrue(hasattr(comms[1], 'sentenceForUUID'))
            self.assertTrue(hasattr(comms[2], 'sentenceForUUID'))
            # assert data still there
            ids = [c.id for c in reader]
            self.assertEquals(['comm-3', 'comm-2', 'comm-1'], ids)
            self.assertEquals(3, redis_db.llen(key))

    def test_set_implicit(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            redis_db.sadd(key, write_communication_to_buffer(self.comm1))
            redis_db.sadd(key, write_communication_to_buffer(self.comm2))
            redis_db.sadd(key, write_communication_to_buffer(self.comm3))
            reader = RedisCommunicationReader(redis_db, key)
            ids = [c.id for c in reader]
            # assert no duplicates
            self.assertEquals(3, len(ids))
            self.assertEquals(set(['comm-1', 'comm-2', 'comm-3']), set(ids))

    def test_list_implicit(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            redis_db.lpush(key, write_communication_to_buffer(self.comm1))
            redis_db.lpush(key, write_communication_to_buffer(self.comm2))
            redis_db.lpush(key, write_communication_to_buffer(self.comm3))
            reader = RedisCommunicationReader(redis_db, key)
            ids = [c.id for c in reader]
            self.assertEquals(['comm-1', 'comm-2', 'comm-3'], ids)

    def test_hash_implicit(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            redis_db.hset(key, self.comm1.uuid.uuidString,
                          write_communication_to_buffer(self.comm1))
            redis_db.hset(key, self.comm2.uuid.uuidString,
                          write_communication_to_buffer(self.comm2))
            redis_db.hset(key, self.comm3.uuid.uuidString,
                          write_communication_to_buffer(self.comm3))
            reader = RedisCommunicationReader(redis_db, key)
            ids = [c.id for c in reader]
            # assert no duplicates
            self.assertEquals(3, len(ids))
            self.assertEquals(set(['comm-1', 'comm-2', 'comm-3']), set(ids))

    def test_set_empty(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            reader = RedisCommunicationReader(redis_db, key, key_type='set')
            self.assertEquals(0, len(reader))
            redis_db.sadd(key, write_communication_to_buffer(self.comm1))
            redis_db.sadd(key, write_communication_to_buffer(self.comm2))
            redis_db.sadd(key, write_communication_to_buffer(self.comm3))
            ids = [c.id for c in reader]
            # assert no duplicates
            self.assertEquals(3, len(ids))
            self.assertEquals(set(['comm-1', 'comm-2', 'comm-3']), set(ids))
            self.assertEquals(3, len(reader))

    def test_list_empty(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            reader = RedisCommunicationReader(redis_db, key, key_type='list')
            self.assertEquals(0, len(reader))
            redis_db.lpush(key, write_communication_to_buffer(self.comm1))
            redis_db.lpush(key, write_communication_to_buffer(self.comm2))
            redis_db.lpush(key, write_communication_to_buffer(self.comm3))
            ids = [c.id for c in reader]
            self.assertEquals(['comm-1', 'comm-2', 'comm-3'], ids)
            self.assertEquals(3, len(reader))

    def test_hash_empty(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            reader = RedisCommunicationReader(redis_db, key, key_type='hash')
            self.assertEquals(0, len(reader))
            redis_db.hset(key, self.comm1.uuid.uuidString,
                          write_communication_to_buffer(self.comm1))
            redis_db.hset(key, self.comm2.uuid.uuidString,
                          write_communication_to_buffer(self.comm2))
            redis_db.hset(key, self.comm3.uuid.uuidString,
                          write_communication_to_buffer(self.comm3))
            ids = [c.id for c in reader]
            # assert no duplicates
            self.assertEquals(3, len(ids))
            self.assertEquals(set(['comm-1', 'comm-2', 'comm-3']), set(ids))
            self.assertEquals(3, len(reader))

    def test_implicit_empty(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            with self.assertRaises(Exception):
                RedisCommunicationReader(redis_db, key)

    def test_set_no_add_references(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            redis_db.sadd(key, write_communication_to_buffer(self.comm1))
            redis_db.sadd(key, write_communication_to_buffer(self.comm2))
            redis_db.sadd(key, write_communication_to_buffer(self.comm3))
            reader = RedisCommunicationReader(redis_db, key, key_type='set',
                                              add_references=False)
            comms = [c for c in reader]
            ids = [c.id for c in comms]
            # assert no duplicates
            self.assertEquals(3, len(ids))
            self.assertEquals(set(['comm-1', 'comm-2', 'comm-3']), set(ids))
            self.assertFalse(hasattr(comms[0], 'sentenceForUUID'))
            self.assertFalse(hasattr(comms[1], 'sentenceForUUID'))
            self.assertFalse(hasattr(comms[2], 'sentenceForUUID'))

    def test_list_no_add_references(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            redis_db.lpush(key, write_communication_to_buffer(self.comm1))
            redis_db.lpush(key, write_communication_to_buffer(self.comm2))
            redis_db.lpush(key, write_communication_to_buffer(self.comm3))
            reader = RedisCommunicationReader(redis_db, key, key_type='list',
                                              add_references=False)
            comms = [c for c in reader]
            ids = [c.id for c in comms]
            self.assertEquals(['comm-1', 'comm-2', 'comm-3'], ids)
            self.assertFalse(hasattr(comms[0], 'sentenceForUUID'))
            self.assertFalse(hasattr(comms[1], 'sentenceForUUID'))
            self.assertFalse(hasattr(comms[2], 'sentenceForUUID'))

    def test_hash_no_add_references(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            redis_db.hset(key, self.comm1.uuid.uuidString,
                          write_communication_to_buffer(self.comm1))
            redis_db.hset(key, self.comm2.uuid.uuidString,
                          write_communication_to_buffer(self.comm2))
            redis_db.hset(key, self.comm3.uuid.uuidString,
                          write_communication_to_buffer(self.comm3))
            reader = RedisCommunicationReader(redis_db, key, key_type='hash',
                                              add_references=False)
            comms = [c for c in reader]
            ids = [c.id for c in comms]
            # assert no duplicates
            self.assertEquals(3, len(ids))
            self.assertEquals(set(['comm-1', 'comm-2', 'comm-3']), set(ids))
            self.assertFalse(hasattr(comms[0], 'sentenceForUUID'))
            self.assertFalse(hasattr(comms[1], 'sentenceForUUID'))
            self.assertFalse(hasattr(comms[2], 'sentenceForUUID'))

    def test_set_pop(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            redis_db.sadd(key, write_communication_to_buffer(self.comm1))
            redis_db.sadd(key, write_communication_to_buffer(self.comm2))
            redis_db.sadd(key, write_communication_to_buffer(self.comm3))
            reader = RedisCommunicationReader(redis_db, key, key_type='set',
                                              pop=True)
            it = iter(reader)
            ids = []
            ids.append(it.next().id)
            ids.append(it.next().id)
            self.assertEquals(1, redis_db.scard(key))
            ids.append(it.next().id)
            # assert no duplicates
            self.assertEquals(3, len(ids))
            self.assertEquals(set(['comm-1', 'comm-2', 'comm-3']), set(ids))
            # assert data is gone
            self.assertEquals([], [c.id for c in reader])
            self.assertFalse(redis_db.exists(key))
            with self.assertRaises(StopIteration):
                it.next()

    def test_list_pop(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            redis_db.lpush(key, write_communication_to_buffer(self.comm1))
            redis_db.lpush(key, write_communication_to_buffer(self.comm2))
            redis_db.lpush(key, write_communication_to_buffer(self.comm3))
            reader = RedisCommunicationReader(redis_db, key, key_type='list',
                                              pop=True)
            it = iter(reader)
            ids = []
            ids.append(it.next().id)
            ids.append(it.next().id)
            self.assertEquals(1, redis_db.llen(key))
            ids.append(it.next().id)
            self.assertEquals(['comm-1', 'comm-2', 'comm-3'], ids)
            # assert data is gone
            self.assertEquals([], [c.id for c in reader])
            self.assertFalse(redis_db.exists(key))
            with self.assertRaises(StopIteration):
                it.next()

    def test_list_pop_left_to_right(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            redis_db.lpush(key, write_communication_to_buffer(self.comm1))
            redis_db.lpush(key, write_communication_to_buffer(self.comm2))
            redis_db.lpush(key, write_communication_to_buffer(self.comm3))
            reader = RedisCommunicationReader(redis_db, key, key_type='list',
                                              pop=True, right_to_left=False)
            it = iter(reader)
            ids = []
            ids.append(it.next().id)
            ids.append(it.next().id)
            self.assertEquals(1, redis_db.llen(key))
            ids.append(it.next().id)
            self.assertEquals(['comm-3', 'comm-2', 'comm-1'], ids)
            # assert data is gone
            self.assertEquals([], [c.id for c in reader])
            self.assertFalse(redis_db.exists(key))
            with self.assertRaises(StopIteration):
                it.next()

    def test_list_block_pop(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            redis_db.lpush(key, write_communication_to_buffer(self.comm1))
            redis_db.lpush(key, write_communication_to_buffer(self.comm2))
            redis_db.lpush(key, write_communication_to_buffer(self.comm3))
            reader = RedisCommunicationReader(redis_db, key, key_type='list',
                                              pop=True, block=True)
            it = iter(reader)
            ids = []
            ids.append(it.next().id)
            ids.append(it.next().id)
            self.assertEquals(1, redis_db.llen(key))
            ids.append(it.next().id)
            self.assertEquals(['comm-1', 'comm-2', 'comm-3'], ids)
            proc = Process(target=_add_comm_to_list,
                           args=(3, server.port, 'comm-4', key))
            proc.start()
            print 'Waiting for new comm to be added (3 sec)...'
            self.assertEquals('comm-4', iter(reader).next().id)
            proc.join()

    def test_list_block_pop_left_to_right(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            redis_db.lpush(key, write_communication_to_buffer(self.comm1))
            redis_db.lpush(key, write_communication_to_buffer(self.comm2))
            redis_db.lpush(key, write_communication_to_buffer(self.comm3))
            reader = RedisCommunicationReader(redis_db, key, key_type='list',
                                              pop=True, block=True,
                                              right_to_left=False)
            it = iter(reader)
            ids = []
            ids.append(it.next().id)
            ids.append(it.next().id)
            self.assertEquals(1, redis_db.llen(key))
            ids.append(it.next().id)
            self.assertEquals(['comm-3', 'comm-2', 'comm-1'], ids)
            proc = Process(target=_add_comm_to_list,
                           args=(3, server.port, 'comm-4', key))
            proc.start()
            print 'Waiting for new comm to be added (3 sec)...'
            self.assertEquals('comm-4', iter(reader).next().id)
            proc.join()

    def test_list_block_pop_timeout(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            redis_db.lpush(key, write_communication_to_buffer(self.comm1))
            redis_db.lpush(key, write_communication_to_buffer(self.comm2))
            redis_db.lpush(key, write_communication_to_buffer(self.comm3))
            reader = RedisCommunicationReader(redis_db, key, key_type='list',
                                              pop=True, block=True,
                                              block_timeout=1)
            it = iter(reader)
            ids = []
            ids.append(it.next().id)
            ids.append(it.next().id)
            self.assertEquals(1, redis_db.llen(key))
            ids.append(it.next().id)
            self.assertEquals(['comm-1', 'comm-2', 'comm-3'], ids)
            with self.assertRaises(StopIteration):
                print 'Waiting for timeout (1 sec)...'
                it.next()


class TestRedisCommunicationWriter(unittest.TestCase):

    def setUp(self):
        self.comm1 = create_comm('comm-1')
        self.comm2 = create_comm('comm-2')
        self.comm3 = create_comm('comm-3')
        self.buf1 = write_communication_to_buffer(self.comm1)
        self.buf2 = write_communication_to_buffer(self.comm2)
        self.buf3 = write_communication_to_buffer(self.comm3)

    def test_set(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            w = RedisCommunicationWriter(redis_db, key, key_type='set')
            w.write(self.comm1)
            self.assertEquals(1, redis_db.scard(key))
            self.assertEquals(self.buf1, redis_db.srandmember(key))
            w.write(self.comm2)
            w.write(self.comm3)
            self.assertEquals(3, redis_db.scard(key))

    def test_list(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            w = RedisCommunicationWriter(redis_db, key, key_type='list')
            w.write(self.comm1)
            self.assertEquals(1, redis_db.llen(key))
            self.assertEquals(self.buf1, redis_db.lindex(key, 0))
            w.write(self.comm2)
            w.write(self.comm3)
            self.assertEquals(3, redis_db.llen(key))
            self.assertEquals(self.buf1, redis_db.lindex(key, -1))
            self.assertEquals(self.buf2, redis_db.lindex(key, -2))
            self.assertEquals(self.buf3, redis_db.lindex(key, -3))

    def test_hash(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            w = RedisCommunicationWriter(redis_db, key, key_type='hash')
            w.write(self.comm1)
            self.assertEquals(1, redis_db.hlen(key))
            self.assertEquals(self.buf1, redis_db.hget(key, self.comm1.id))
            w.write(self.comm2)
            w.write(self.comm3)
            self.assertEquals(3, redis_db.hlen(key))
            self.assertEquals(self.buf1, redis_db.hget(key, self.comm1.id))
            self.assertEquals(self.buf2, redis_db.hget(key, self.comm2.id))
            self.assertEquals(self.buf3, redis_db.hget(key, self.comm3.id))

    def test_hash_uuid_key(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            w = RedisCommunicationWriter(
                redis_db, key, key_type='hash', uuid_hash_key=True)
            w.write(self.comm1)
            self.assertEquals(1, redis_db.hlen(key))
            self.assertEquals(self.buf1, redis_db.hget(
                key, self.comm1.uuid.uuidString))
            w.write(self.comm2)
            w.write(self.comm3)
            self.assertEquals(3, redis_db.hlen(key))
            self.assertEquals(self.buf1, redis_db.hget(
                key, self.comm1.uuid.uuidString))
            self.assertEquals(self.buf2, redis_db.hget(
                key, self.comm2.uuid.uuidString))
            self.assertEquals(self.buf3, redis_db.hget(
                key, self.comm3.uuid.uuidString))

    def test_list_left_to_right(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            w = RedisCommunicationWriter(redis_db, key, key_type='list',
                                         right_to_left=False)
            w.write(self.comm1)
            self.assertEquals(1, redis_db.llen(key))
            self.assertEquals(self.buf1, redis_db.lindex(key, 0))
            w.write(self.comm2)
            w.write(self.comm3)
            self.assertEquals(3, redis_db.llen(key))
            self.assertEquals(self.buf3, redis_db.lindex(key, -1))
            self.assertEquals(self.buf2, redis_db.lindex(key, -2))
            self.assertEquals(self.buf1, redis_db.lindex(key, -3))

    def test_set_implicit(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            redis_db.sadd(key, self.buf1)
            w = RedisCommunicationWriter(redis_db, key)
            w.write(self.comm2)
            w.write(self.comm3)
            self.assertEquals(3, redis_db.scard(key))

    def test_list_implicit(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            redis_db.lpush(key, self.buf1)
            w = RedisCommunicationWriter(redis_db, key)
            w.write(self.comm2)
            w.write(self.comm3)
            self.assertEquals(3, redis_db.llen(key))
            self.assertEquals(self.buf1, redis_db.lindex(key, -1))
            self.assertEquals(self.buf2, redis_db.lindex(key, -2))
            self.assertEquals(self.buf3, redis_db.lindex(key, -3))

    def test_hash_implicit(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            redis_db.hset(key, self.comm1.id, self.buf1)
            w = RedisCommunicationWriter(redis_db, key)
            w.write(self.comm2)
            w.write(self.comm3)
            self.assertEquals(3, redis_db.hlen(key))
            self.assertEquals(self.buf1, redis_db.hget(key, self.comm1.id))
            self.assertEquals(self.buf2, redis_db.hget(key, self.comm2.id))
            self.assertEquals(self.buf3, redis_db.hget(key, self.comm3.id))

    def test_implicit_empty(self):
        key = 'dataset'
        with RedisServer(loglevel='warning') as server:
            redis_db = Redis(port=server.port)
            with self.assertRaises(Exception):
                RedisCommunicationWriter(redis_db, key)
