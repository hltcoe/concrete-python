#!/usr/bin/env python

import unittest
from redis import Redis

from concrete.util import (
    read_communication_from_file,
    read_communication_from_buffer,
    read_communication_from_redis_key,
    RedisCommunicationReader,
    write_communication_to_buffer,
    write_communication_to_redis_key,
    RedisCommunicationWriter,
)
from concrete.util.simple_comm import create_simple_comm
from concrete.util.redis_server import RedisServer


class TestReadCommunicationFromBuffer(unittest.TestCase):
    def test_read_against_file_contents(self):
        filename = u'tests/testdata/simple_1.concrete'
        with open(filename, 'rb') as f:
            buf = f.read()
            comm = read_communication_from_buffer(buf)
            self.assertEquals('one', comm.id)


class TestWriteCommunicationToBuffer(unittest.TestCase):
    def test_write_against_file_contents(self):
        filename = u'tests/testdata/simple_1.concrete'
        with open(filename, 'rb') as f:
            f_buf = f.read()
            comm = read_communication_from_buffer(f_buf)
        buf = write_communication_to_buffer(comm)
        self.assertEquals(f_buf, buf)

    def test_read_write_fixed_point(self):
        comm = create_simple_comm('comm-1')
        buf_1 = write_communication_to_buffer(comm)
        buf_2 = write_communication_to_buffer(
            read_communication_from_buffer(buf_1)
        )
        self.assertEquals(buf_1, buf_2)


class TestRedisCommunicationReader(unittest.TestCase):
    def test_set_iter_implicit(self):
        key = 'dataset'
        comm1 = create_simple_comm('comm-1')
        comm2 = create_simple_comm('comm-2')
        comm3 = create_simple_comm('comm-3')
        with RedisServer() as server:
            redis_db = Redis(port=server.port)
            redis_db.sadd(key, write_communication_to_buffer(comm1))
            redis_db.sadd(key, write_communication_to_buffer(comm2))
            redis_db.sadd(key, write_communication_to_buffer(comm3))
            reader = RedisCommunicationReader(redis_db, key)
            ids = [c.id for c in reader]
            self.assertEquals(3, len(ids))
            self.assertEquals(set(['comm-1', 'comm-2', 'comm-3']), set(ids))

    def test_list_iter_implicit(self):
        key = 'dataset'
        comm1 = create_simple_comm('comm-1')
        comm2 = create_simple_comm('comm-2')
        comm3 = create_simple_comm('comm-3')
        with RedisServer() as server:
            redis_db = Redis(port=server.port)
            redis_db.rpush(key, write_communication_to_buffer(comm1))
            redis_db.rpush(key, write_communication_to_buffer(comm2))
            redis_db.rpush(key, write_communication_to_buffer(comm3))
            reader = RedisCommunicationReader(redis_db, key)
            ids = [c.id for c in reader]
            self.assertEquals(['comm-1', 'comm-2', 'comm-3'], ids)

    def test_hash_iter_implicit(self):
        key = 'dataset'
        comm1 = create_simple_comm('comm-1')
        comm2 = create_simple_comm('comm-2')
        comm3 = create_simple_comm('comm-3')
        with RedisServer() as server:
            redis_db = Redis(port=server.port)
            redis_db.hset(key, comm1.uuid.uuidString,
                          write_communication_to_buffer(comm1))
            redis_db.hset(key, comm2.uuid.uuidString,
                          write_communication_to_buffer(comm2))
            redis_db.hset(key, comm3.uuid.uuidString,
                          write_communication_to_buffer(comm3))
            reader = RedisCommunicationReader(redis_db, key)
            ids = [c.id for c in reader]
            self.assertEquals(3, len(ids))
            self.assertEquals(set(['comm-1', 'comm-2', 'comm-3']), set(ids))

    def test_set_iter_explicit(self):
        key = 'dataset'
        comm1 = create_simple_comm('comm-1')
        comm2 = create_simple_comm('comm-2')
        comm3 = create_simple_comm('comm-3')
        with RedisServer() as server:
            redis_db = Redis(port=server.port)
            redis_db.sadd(key, write_communication_to_buffer(comm1))
            redis_db.sadd(key, write_communication_to_buffer(comm2))
            redis_db.sadd(key, write_communication_to_buffer(comm3))
            reader = RedisCommunicationReader(redis_db, key, key_type='set')
            ids = [c.id for c in reader]
            self.assertEquals(3, len(ids))
            self.assertEquals(set(['comm-1', 'comm-2', 'comm-3']), set(ids))

    def test_list_iter_explicit(self):
        key = 'dataset'
        comm1 = create_simple_comm('comm-1')
        comm2 = create_simple_comm('comm-2')
        comm3 = create_simple_comm('comm-3')
        with RedisServer() as server:
            redis_db = Redis(port=server.port)
            redis_db.rpush(key, write_communication_to_buffer(comm1))
            redis_db.rpush(key, write_communication_to_buffer(comm2))
            redis_db.rpush(key, write_communication_to_buffer(comm3))
            reader = RedisCommunicationReader(redis_db, key, key_type='list')
            ids = [c.id for c in reader]
            self.assertEquals(['comm-1', 'comm-2', 'comm-3'], ids)

    def test_hash_iter_explicit(self):
        key = 'dataset'
        comm1 = create_simple_comm('comm-1')
        comm2 = create_simple_comm('comm-2')
        comm3 = create_simple_comm('comm-3')
        with RedisServer() as server:
            redis_db = Redis(port=server.port)
            redis_db.hset(key, comm1.uuid.uuidString,
                          write_communication_to_buffer(comm1))
            redis_db.hset(key, comm2.uuid.uuidString,
                          write_communication_to_buffer(comm2))
            redis_db.hset(key, comm3.uuid.uuidString,
                          write_communication_to_buffer(comm3))
            reader = RedisCommunicationReader(redis_db, key, key_type='hash')
            ids = [c.id for c in reader]
            self.assertEquals(3, len(ids))
            self.assertEquals(set(['comm-1', 'comm-2', 'comm-3']), set(ids))


if __name__ == '__main__':
    unittest.main(buffer=True)
