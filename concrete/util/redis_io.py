import string
import random
import time

from thrift.protocol.TCompactProtocol import TCompactProtocol
from thrift.transport.TTransport import TMemoryBuffer

from concrete import Communication
from concrete.util.references import add_references_to_communication


def read_communication_from_buffer(buf, add_references=True):
    '''
    Deserialize buf and return resulting communication.
    Add references if requested.
    '''
    transport_in = TMemoryBuffer(buf)
    protocol_in = TCompactProtocol(transport_in)
    comm = Communication()
    comm.read(protocol_in)
    if add_references:
        add_references_to_communication(comm)
    return comm


def read_communication_from_redis_key(redis_db, key, add_references=True):
    '''
    Return a serialized communication from a string key.  If block
    is True, poll server until key appears at specified interval
    or until specified timeout (indefinitely if timeout is zero).
    Return None if block is False and key does not exist or if
    block is True and key does not exist after specified timeout.
    '''
    buf = redis_db.get(key)
    if buf is None:
        return None
    else:
        return read_communication_from_buffer(buf,
                                              add_references=add_references)


class RedisCommunicationReader(object):
    '''
    Iterable class for reading one or more Communications from redis.

    Supported input types are:

    - a set containing zero or more Communications
    - a list containing zero or more Communications
    - a hash containing zero or more UUID-Communication key-value pairs

    For list and set types, the reader can optionally pop (consume) its
    input; for lists only, the reader can moreover block on the input.

    Note that iteration over a set or hash will create a temporary key
    in the redis database to maintain a set of elements scanned so far.

    If pop is False and the key (in the database) is modified during
    iteration, behavior is undefined.  If pop is True, modifications
    during iteration are encouraged. :)

    Example usage:

        from redis import Redis
        redis_db = Redis(port=12345)
        for comm in RedisCommunicationReader(redis_db, 'my_comm_set_key'):
            do_something(comm)
    '''

    def __init__(self, redis_db, key, key_type=None, pop=False, block=False,
                 right_to_left=True, add_references=True,
                 block_timeout=0, temp_key_ttl=3600, temp_key_leaf_len=32):
        '''
        Create communication reader for specified key in specified
        redis_db.

            redis_db: object of class redis.Redis
            key:      name of redis key containing your communication(s)
            key_type: 'set', 'list', 'hash', or None; if None, look up
                      type in redis (only works if the key exists, so
                      probably not suitable for block and/or pop modes)
            pop:      boolean, True to remove communications from redis
                      as we iterate over them, and False to leave redis
                      unaltered
            block:    boolean, True to block for data (i.e., wait for
                      something to be added to the list if it is empty),
                      False to end iteration when there is no more data
            right_to_left: boolean, True to iterate over and index in
                      lists from right to left, False to iterate/index
                      from left to right
            add_references: boolean, True to fill in members in the
                      communication according to UUID relationships (see
                      concrete.util.add_references), False to return
                      communication as-is (note: you may need this False
                      if you are dealing with incomplete communications)
        '''
        self.redis_db = redis_db
        self.key = key

        if key_type is None:
            # try to guess type
            if redis_db.exists(key):
                key_type = redis_db.type(key)
            else:
                raise ValueError('can only guess type of key that exists')

        if key_type not in ('set', 'hash', 'list'):
            raise ValueError('unrecognized key type %s' % key_type)

        self.key_type = key_type

        if pop and key_type not in ('set', 'list'):
            raise ValueError('can only pop on set or list')
        if block and key_type not in ('list',):
            raise ValueError('can only pop on set or list')
        if block and not pop:
            raise ValueError('can only block if popping too')

        self.pop = pop
        self.block = block
        self.block_timeout = block_timeout

        self.temp_key_ttl = temp_key_ttl
        self.temp_key_leaf_len = temp_key_leaf_len

        self.right_to_left = right_to_left
        self.add_references = add_references

    def __iter__(self):
        if self.key_type in ('list', 'set') and self.pop:
            buf = self._pop_buf()
            while buf is not None:
                yield self._load_from_buffer(buf)
                buf = self._pop_buf()

        elif self.key_type == 'list' and not self.pop:
            for i in xrange(self.redis_db.llen(self.key)):
                idx = -(i+1) if self.right_to_left else i
                buf = self.redis_db.lindex(self.key, idx)
                yield self._load_from_buffer(buf)

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

    def __len__(self):
        '''
        Return instantaneous length of dataset.
        '''
        if self.key_type == 'list':
            return self.redis_db.llen(self.key)
        elif self.key_type == 'set':
            return self.redis_db.scard(self.key)
        elif self.key_type == 'hash':
            return self.redis_db.hlen(self.key)
        else:
            raise Exception('not implemented')

    def __getitem__(self, k):
        '''
        Return item at specified list index or hash key (UUID);
        never pop or block.
        '''
        if self.key_type in ('list', 'hash'):
            if self.key_type == 'list':
                idx = -(k+1) if self.right_to_left else k
                buf = self.redis_db.lindex(self.key, idx)
            else:
                buf = self.redis_db.hget(self.key, k)
            return None if buf is None else self._load_from_buffer(buf)

        else:
            raise Exception('not implemented')

    def batch(self, n):
        '''
        Return a batch of n communications.  May be faster than
        one-at-a-time iteration, but currently only supported for
        non-popping, non-blocking set configurations.  Support for
        popping, non-blocking sets is planned; see
        http://redis.io/commands/spop .
        '''
        if self.key_type == 'set' and not self.pop and not self.block:
            return [
                self._load_from_buffer(buf)
                for buf
                in self.redis_db.srandmember(self.key, n)
            ]

        else:
            raise Exception('not implemented')

    def _pop_buf(self):
        '''
        Pop and return a serialized communication, or None if there is
        none (or we blocked and timed out).
        '''
        if self.key_type == 'list':
            if self.block:
                _pop = (
                    self.redis_db.brpop
                    if self.right_to_left
                    else self.redis_db.blpop
                )
                val = _pop(self.key, timeout=self.block_timeout)
                return None if val is None else val[1]
            else:
                _pop = (
                    self.redis_db.rpop
                    if self.right_to_left
                    else self.redis_db.lpop
                )
                return _pop(self.key)

        elif self.key_type == 'set' and not self.block:
            return self.redis_db.spop(self.key)

        else:
            raise Exception('not implemented')

    def _load_from_buffer(self, buf):
        return read_communication_from_buffer(buf, add_references=self.add_references)

    def _make_temp_key(self):
        '''
        Generate temporary (random, unused) key.  Do not set in redis
        (leave that to the caller).
        '''
        temp_key = None
        while temp_key is None or self.redis_db.exists(temp_key):
            # thanks: http://stackoverflow.com/a/2257449
            temp_key_leaf = ''.join(
                random.choice(string.ascii_lowercase + string.digits)
                for _ in range(self.temp_key_leaf_len)
            )
            temp_key = ':'.join(('temp', self.key, temp_key_leaf))
        return temp_key

    def __str__(self):
        return '%s(%s, %s, %s)' % (type(self).__name__, self.redis_db,
                                   self.key, self.key_type)


def write_communication_to_buffer(comm):
    '''
    Serialize communication and return result.
    '''
    transport = TMemoryBuffer()
    protocol = TCompactProtocol(transport)
    comm.write(protocol)
    return transport.getvalue()


def write_communication_to_redis_key(redis_db, key, comm):
    '''
    Serialize communication and store result in redis key.
    '''
    redis_db.set(key, write_communication_to_buffer(comm))


class RedisCommunicationWriter(object):
    '''
    Class for writing one or more Communications to redis.

    Supported input types are:

    - a set of Communications
    - a list of Communications
    - a hash of UUID-Communication key-value pairs

    Example usage:

        from redis import Redis
        redis_db = Redis(port=12345)
        w = RedisCommunicationWriter(redis_db, 'my_comm_set_key')
        w.write(comm)
    '''

    def __init__(self, redis_db, key, key_type=None, right_to_left=True):
        '''
        Create communication writer for specified key in specified
        redis_db.

            redis_db: object of class redis.Redis
            key:      name of redis key containing your communication(s)
            key_type: 'set', 'list', 'hash', or None; if None, look up
                      type in redis (only works if the key exists)
            right_to_left: boolean, True to write elements to the left
                      end of lists, False to write to the right end
        '''
        self.redis_db = redis_db
        self.key = key

        if key_type is None:
            # try to guess type
            if redis_db.exists(key):
                key_type = redis_db.type(key)
            else:
                raise ValueError('can only guess type of key that exists')

        if key_type not in ('set', 'hash', 'list'):
            raise ValueError('unrecognized key type %s' % key_type)

        self.key_type = key_type
        self.right_to_left = right_to_left

    def clear(self):
        self.redis_db.delete(self.key)

    def write(self, comm):
        buf = self._write_to_buffer(comm)

        if self.key_type == 'list':
            _push = (
                self.redis_db.lpush
                if self.right_to_left
                else self.redis_db.rpush
            )
            return _push(self.key, buf)

        elif self.key_type == 'set':
            return self.redis_db.sadd(self.key, buf)

        elif self.key_type == 'hash':
            return self.redis_db.hset(self.key, comm.uuid.uuidString, buf)

        else:
            raise Exception('not implemented')

    def _write_to_buffer(self, comm):
        return write_communication_to_buffer(comm)

    def __str__(self):
        return '%s(%s, %s, %s)' % (type(self).__name__, self.redis_db,
                                   self.key, self.key_type)
