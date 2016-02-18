import subprocess
import redis
import time

from concrete.util.net import find_port


def start_redis(*args, **kwargs):
    '''
    Start redis server using specified arguments and return tuple:
    (subprocess.Popen object, redis.Redis object, port).  Arguments
    are the same as redis-server command-line arguments, except two
    hyphens are automatically prepended to all keys in kwargs.
    Example usage:

    >>> (p, r, port) = start_redis(logfile='/dev/null')
    >>> stop_redis(p, r)
    '''
    cmd = ['redis-server']
    if 'port' in kwargs:
        port = int(kwargs['port'])
    else:
        port = find_port()
        cmd.extend(['--port', str(port)])
    for (k, v) in kwargs.items():
        cmd.extend(['--%s' % k, str(v)])
    cmd.extend(args)
    p = subprocess.Popen(cmd)
    r = redis.Redis(port=port)
    while True:
        time.sleep(0.1)
        try:
            ret = r.ping()
        except redis.ConnectionError:
            pass
        else:
            if ret:
                break
    return (p, r, port)


def stop_redis(p, r):
    '''
    Shut down redis server.  r should be a redis.Redis object; p should
    be a subprocess.Popen object.
    '''
    r.shutdown()
    p.wait()


class RedisServer(object):
    '''
    Redis server context manager.  Class members are:

        popen:  subprocess.Popen object for server
        client: redis.Redis object connected to server
        port:   port number of server

    Example usage:

    >>> n = None
    >>> elt = None
    >>> with RedisServer(logfile='/dev/null') as server:
    ...     n = server.client.lpush('foo', 'bar', 'baz', 'bbq')
    ...     elt = server.client.rpop('foo')
    >>> n
    3L
    >>> elt
    'bar'
    '''

    def __init__(self, *args, **kwargs):
        self.popen = None
        self.client = None
        self.port = None
        self._args = args
        self._kwargs = kwargs

    def __enter__(self):
        (self.popen, self.client, self.port) = start_redis(
            *self._args, **self._kwargs)
        return self

    def __exit__(self, type, value, traceback):
        stop_redis(self.popen, self.client)
