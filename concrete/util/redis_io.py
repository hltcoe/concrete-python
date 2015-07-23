"""Code for reading and writing Concrete Communications
"""

import string
import random

from thrift.protocol.TCompactProtocol import TCompactProtocol
from thrift.transport.TTransport import TMemoryBuffer

from concrete import Communication
from concrete.util.references import add_references_to_communication

class CommunicationReader(object):
    '''
    Iterable class for reading one or more Communications from redis.

    Supported types are:

    - a string containing a Communication
    - a set containing zero or more Communications
    - a list containing zero or more Communications
    - a hash containing zero or more UUID-Communication key-value pairs

    For list and set types, the reader can optionally pop (consume) its
    input; for lists only, the reader can moreover block on the input.

    Note that iteration over a set or hash will create a temporary key
    in the redis database to maintain a set of elements seen so far.

    -----

    Sample usage:

        for comm in CommunicationReader(Redis(), 'my_comm_set'):
            do_something(comm)
    '''
    def __init__(self, redis_db, key, key_type=None, pop=False, block=False,
                 timeout=0,
                 temp_key_ttl=3600, temp_key_leaf_len=32, add_references=True):
        self.redis_db = redis_db
        self.key = key

        if key_type is None:
            # try to guess type
            if redis_db.exists(key):
                key_type = redis_db.type(key)
            else:
                raise ValueError('can only guess type of key that exists')

        if key_type not in ('set', 'hash', 'string', 'list'):
            raise ValueError('unrecognized key type %s' % key_type)

        self.key_type = key_type

        if pop and key_type not in ('set', 'list'):
            raise ValueError('can only pop on set or list')
        if block and not pop:
            raise ValueError('can only block if popping too')

        self.pop = pop
        self.block = block
        self.timeout = timeout

        self.temp_key_ttl = temp_key_ttl
        self.temp_key_leaf_len = temp_key_leaf_len

        self.add_references = add_references

    def __iter__(self):
        if self.key_type in ('list', 'set') and self.pop:
            buf = self._pop_buf()
            while buf is not None:
                yield self._load_from_buffer(buf)
                buf = self._pop_buf()

        elif self.key_type == 'list' and not self.pop:
            for i in xrange(self.redis_db.llen(self.key)):
                yield self._load_from_buffer(self.redis_db.lindex(i))

        elif self.key_type in ('set', 'hash') and not self.pop:
            if self.key_type == 'set':
                num_comms = self.redis_db.scard(self.key)
                scan = self.redis_db.sscan
                # batch is an iterable of buffers
                get_comm = lambda k, batch: self._load_from_buffer(k)
            else:
                num_comms = self.redis_db.hlen(self.key)
                scan = self.redis_db.hscan
                # batch is a dict of uuid-buffer key-value pairs
                get_comm = lambda k, batch: self._load_from_buffer(batch[k])

            temp_key = self._make_temp_key()

            i = 0
            cursor = 0
            while i < num_comms:
                (cursor, batch) = scan(self.key, cursor)
                for k in batch:
                    if i == num_comms:
                        break
                    if self.redis_db.sadd(temp_key, k) > 0:
                        i += 1
                        yield get_comm(k, batch)
                    self.redis_db.expire(temp_key, self.temp_key_ttl)

        else:
            raise Exception('not implemented')

    def get(self, k):
        if self.key_type in ('list', 'hash'):
            if self.key_type == 'list':
                buf = self.redis_db.lindex(self.key, k)
            else:
                buf = self.redis_db.hget(self.key, k)
            return None if buf is None else self._load_from_buffer(buf)

        else:
            raise Exception('not implemented')

    def sample(self, n=1):
        if self.key_type in ('list', 'set') and self.pop:
            return [
                self._load_from_buffer(buf)
                for buf
                in (
                    self._pop_buf()
                    for i
                    in xrange(n)
                )
                if buf is not None
            ]

        elif self.key_type == 'set' and not self.pop:
            return [
                self._load_from_buffer(buf)
                for buf
                in self.redis_db.srandmember(self.key, n)
            ]

        else:
            raise Exception('not implemented')

    def _pop_buf():
        if self.key_type == 'list':
            if self.block:
                val = self.redis_db.brpop(self.key, timeout=self.timeout)
                return None if val is None else val[1]
            else:
                return self.redis_db.rpop(self.key)

        elif self.key_type == 'set' and not self.block:
            return self.redis_db.spop(self.key)

        else:
            raise Exception('not implemented')

    def _make_temp_key(self):
        temp_key = None
        while temp_key is None or self.redis_db.exists(temp_key):
            # thanks: http://stackoverflow.com/a/2257449
            temp_key_leaf = ''.join(
                random.choice(string.ascii_lowercase + string.digits)
                for _ in range(self.temp_key_leaf_len)
            )
            temp_key = ':'.join(('temp', self.key, temp_key_leaf))
        return temp_key

    def _load_from_buffer(self, buf):
        transport_in = TMemoryBuffer(buf)
        protocol_in = TCompactProtocol(transport_in)
        comm = Communication()
        comm.read(protocol_in)
        if self.add_references:
            add_references_to_communication(comm)
        return comm

    def __str__(self):
        return '%s(%s, %s, %s)' % (type(self).__name__, self.redis_db,
                                   self.key, self.key_type)
