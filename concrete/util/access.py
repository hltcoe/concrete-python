from __future__ import unicode_literals
import logging
import os
from hashlib import md5

from ..access.ttypes import FetchResult
from ..services.ttypes import ServiceInfo
from .access_wrapper import FetchCommunicationClientWrapper
from .file_io import write_communication_to_file
from .mem_io import write_communication_to_buffer
from .redis_io import RedisCommunicationWriter
from ..version import concrete_library_version


DEFAULT_S3_KEY_PREFIX_LEN = 4


class CommunicationContainerFetchHandler(object):
    """FetchCommunicationService implementation using Communication containers

    Implements the :mod:`.FetchCommunicationService` interface, retrieving
    Communications from a dict-like `communication_container` object
    that maps Communication ID strings to Communications.  The
    `communication_container` could be an actual dict, or a container
    such as:

    - :class:`.DirectoryBackedCommunicationContainer`
    - :class:`.FetchBackedCommunicationContainer`
    - :class:`.MemoryBackedCommunicationContainer`
    - :class:`.RedisHashBackedCommunicationContainer`
    - :class:`.ZipFileBackedCommunicationContainer`
    - :class:`.S3BackedCommunicationContainer`

    Usage::

        from concrete.util.access_wrapper import FetchCommunicationServiceWrapper

        handler = CommunicationContainerFetchHandler(comm_container)
        fetch_service = FetchCommunicationServiceWrapper(handler)
        fetch_service.serve(host, port)
    """

    def __init__(self, communication_container):
        """
        Args:
            communication_container: Dict-like object that maps Communication
                                     IDs to Communications
        """
        self.communication_container = communication_container

    def about(self):
        logging.debug("Received about() call")
        service_info = ServiceInfo()
        service_info.name = 'CommunicationContainerFetchHandler - %s' % \
                            type(self.communication_container)
        service_info.version = concrete_library_version()
        return service_info

    def alive(self):
        logging.debug("Received alive() call")
        return True

    def fetch(self, fetch_request):
        logging.debug("Received FetchRequest: %s" % fetch_request)
        fetch_result = FetchResult()
        fetch_result.communications = []
        for communication_id in fetch_request.communicationIds:
            if communication_id in self.communication_container:
                comm = self.communication_container[communication_id]
                fetch_result.communications.append(comm)
            else:
                logging.warning('Unable to find Communication with ID: %s' % communication_id)
        return fetch_result

    def getCommunicationCount(self):
        logging.debug('Received getCommunicationCount()')
        communicationCount = len(self.communication_container)
        logging.debug('- Communication Count: %d' % communicationCount)
        return communicationCount

    def getCommunicationIDs(self, offset, count):
        logging.debug('Received getCommunicationIDs() call')
        return list(self.communication_container.keys())[offset:][:count]


class DirectoryBackedStoreHandler(object):
    """Simple StoreCommunicationService implementation using a directory

    Implements the :mod:`.StoreCommunicationService` interface, storing
    Communications in a directory.
    """
    def __init__(self, store_path):
        """
        Args:
            store_path: Path where Communications should be Stored
        """
        self.store_path = store_path

    def about(self):
        logging.debug("DirectoryBackedStoreHandler.about() called")
        service_info = ServiceInfo()
        service_info.name = 'DirectoryBackedStoreHandler'
        service_info.version = concrete_library_version()
        return service_info

    def alive(self):
        logging.debug("DirectoryBackedStoreHandler.alive() called")
        return True

    def store(self, communication):
        """Save Communication to a directory

        Stored Communication files will be named `[COMMUNICATION_ID].comm`.
        If a file with that name already exists, it will be overwritten.
        """
        logging.debug(
            "DirectoryBackedStoreHandler.store() called with Communication "
            "with ID '%s'" % communication.id)
        comm_filename = os.path.join(self.store_path, communication.id + '.comm')
        write_communication_to_file(communication, comm_filename)


class RelayFetchHandler(object):
    """Implements a 'relay' to another :mod:`.FetchCommunicationService`
    server.

    A :mod:`.FetchCommunicationService` that acts as a relay to a
    second :mod:`.FetchCommunicationService`, where the second
    service is using the TSocket transport and TCompactProtocol
    protocol.

    This class was designed for the use case where you have Thrift
    JavaScript code that needs to communicate with a
    :mod:`.FetchCommunicationService` server, but the server does
    not support the same Thrift serialization protocol as the
    JavaScript client.

    The de-facto standard for Concrete services is to use the
    TCompactProtocol serialization protocol over a TSocket connection.
    But as of Thrift 0.10.0, the Thrift JavaScript libraries only
    support using TJSONProtocol over HTTP.

    The RelayFetchHandler class is intended to be used as server-side
    code by a web application.  The JavaScript code will make
    :mod:`.FetchCommunicationService` RPC calls to the web server
    using HTTP/TJSONProtocol, and the web application will then pass
    these RPC calls to another :mod:`.FetchCommunicationService`
    using TSocket/TCompactProtocol RPC calls.
    """
    def __init__(self, host, port):
        """
        Args:
            host (str): Hostname of :mod:`.FetchCommunicationService` server
            port (int): Port # of :mod:`.FetchCommunicationService` server
        """
        self.host = host
        self.port = int(port)

    def about(self):
        logging.debug('RelayFetchHandler.about()')
        with FetchCommunicationClientWrapper(self.host, self.port) as fc:
            return fc.about()

    def alive(self):
        logging.debug('RelayFetchHandler.alive()')
        with FetchCommunicationClientWrapper(self.host, self.port) as fc:
            return fc.alive()

    def fetch(self, request):
        logging.debug('RelayFetchHandler.fetch()')
        with FetchCommunicationClientWrapper(self.host, self.port) as fc:
            return fc.fetch(request)

    def getCommunicationCount(self):
        logging.debug('RelayFetchHandler.getCommunicationCount()')
        with FetchCommunicationClientWrapper(self.host, self.port) as fc:
            return fc.getCommunicationCount()

    def getCommunicationIDs(self, offset, count):
        logging.debug('RelayFetchHandler.getCommunicationIDs(offset=%d, count=%d)' %
                      (offset, count))
        with FetchCommunicationClientWrapper(self.host, self.port) as fc:
            return fc.getCommunicationIDs(offset, count)


def prefix_s3_key(key_str, prefix_len):
    '''
    Given unprefixed S3 key `key_str`, prefix the key with a
    deterministic prefix of hex characters of length `prefix_len` and
    return the result.  Keys with such prefixes enable better
    performance on S3 and reduce the likelihood of rate-limiting.

    Args:
        key_str (str): original (unprefixed) key, as a string
        prefix_len (int): length of prefix to add to key

    Returns:
        prefixed key

    References:
        http://docs.aws.amazon.com/AmazonS3/latest/dev/request-rate-perf-considerations.html
    '''
    return md5(key_str.encode('utf-8')).hexdigest()[:prefix_len] + key_str


def unprefix_s3_key(prefixed_key_str, prefix_len):
    '''
    Given prefixed S3 key `key_str`, remove prefix of length
    `prefix_len` from the key and return the result.
    Keys with random-looking prefixes enable better performance on S3
    and reduce the likelihood of rate-limiting.

    Args:
        preixed_key_str (str): prefixed key, as a string
        prefix_len (int): length of prefix to remove from key

    Returns:
        unprefixed key

    References:
        http://docs.aws.amazon.com/AmazonS3/latest/dev/request-rate-perf-considerations.html
    '''
    return prefixed_key_str[prefix_len:]


class S3BackedStoreHandler(object):
    """Simple StoreCommunicationService implementation using an AWS S3
    bucket.

    Implements the :mod:`.StoreCommunicationService` interface, storing
    Communications in an S3 bucket, indexed by id, optionally prefixed
    with a fixed-length, random-looking but deterministic hash to
    improve performance.

    References:
        http://docs.aws.amazon.com/AmazonS3/latest/dev/request-rate-perf-considerations.html
    """
    def __init__(self, bucket, prefix_len=DEFAULT_S3_KEY_PREFIX_LEN):
        """
        Args:
            bucket (boto.s3.bucket.Bucket): S3 bucket object
            prefix_len (int): length of prefix to add to
                a Communication id to form its key.  A
                prefix of length four enables S3 to better partition the
                bucket contents, yielding higher performance and a lower
                chance of getting rate-limited by AWS.
        """
        self.bucket = bucket
        self.prefix_len = prefix_len

    def about(self):
        """
        Return S3BackedStoreHandler service information.

        Returns:
            An object of type :class:`.ServiceInfo`
        """
        logging.debug("S3BackedStoreHandler.about() called")
        service_info = ServiceInfo()
        service_info.name = 'S3BackedStoreHandler'
        service_info.version = concrete_library_version()
        return service_info

    def alive(self):
        """
        Return whether service is alive and running.

        Returns:
            True or False
        """
        logging.debug("S3BackedStoreHandler.alive() called")
        return True

    def store(self, communication):
        """
        Save Communication to an S3 bucket, using the Communication
        id with a hash prefix of length `self.prefix_len`
        as a key.

        Args:
            communication (Communication): communication to store
        """
        logging.debug(
            "S3BackedStoreHandler.store() called with Communication "
            "with ID '%s'" % communication.id)
        buf = write_communication_to_buffer(communication)
        prefixed_key_str = prefix_s3_key(communication.id, self.prefix_len)
        key = self.bucket.get_key(prefixed_key_str, validate=False)
        key.set_contents_from_string(buf)


class RedisHashBackedStoreHandler(object):
    """Simple StoreCommunicationService implementation using a Redis
    hash.

    Implements the :mod:`.StoreCommunicationService` interface, storing
    Communications in a Redis hash, indexed by id.
    """
    def __init__(self, redis_db, key):
        """
        Args:
            redis_db (redis.Redis): Redis database connection object
            key (str): key of hash in redis database
        """
        self.writer = RedisCommunicationWriter(redis_db, key, key_type='hash')

    def about(self):
        logging.debug("RedisHashBackedStoreHandler.about() called")
        service_info = ServiceInfo()
        service_info.name = 'RedisHashBackedStoreHandler'
        service_info.version = concrete_library_version()
        return service_info

    def alive(self):
        logging.debug("RedisHashBackedStoreHandler.alive() called")
        return True

    def store(self, communication):
        """Save Communication to a Redis hash, using the Communication
        id as a key.

        Args:
            communication (Communication): communication to store
        """
        logging.debug(
            "RedisHashBackedStoreHandler.store() called with Communication "
            "with ID '%s'" % communication.id)
        self.writer.write(communication)
