"""Communication Containers - mapping Communication IDs to Communications

Classes that behave like a read-only dictionary (implementing Python's
`collections.Mapping` interface) and map Communication ID strings to
Communications.

The classes abstract away the storage backend.  If you need to
optimize for performance, you may not want to use a dictionary
abstraction that retrieves one Communication at a time.
"""
from __future__ import unicode_literals

import collections
import gzip
import logging
import os
import zipfile

import humanfriendly

from ..access.ttypes import FetchRequest
from .access_wrapper import FetchCommunicationClientWrapper
from .file_io import (
    CommunicationReader,
    read_communication_from_file)
from .mem_io import read_communication_from_buffer


class DirectoryBackedCommunicationContainer(collections.Mapping):
    """Maps Comm IDs to Comms, retrieving Comms from the filesystem

    `DirectoryBackedCommunicationContainer` instances behave as
    dict-like data structures that map Communication IDs to
    Communications.  Communications are lazily-retrieved from the
    filesystem.

    Upon initialization, a `DirectoryBackedCommunicationContainer`
    instance will (recursively) search `directory_path` for any files
    that end with the specified `comm_extensions`.  Files with
    matching extensions are assumed to be Communication files whose
    filename (sans extension) is the file's Communication ID.  So, for
    example, a file named 'XIN_ENG_20101212.0120.concrete' is assumed
    to be a Communication file with a Communication ID of
    'XIN_ENG_20101212.0120'.

    Files with the extension `.gz` will be decompressed using gzip.

    A `DirectoryBackedCommunicationsContainer` will not be able to find
    any files that are added to `directory_path` after the container
    was initialized.
    """

    def __init__(self, directory_path,
                 comm_extensions=['.comm', '.concrete', '.gz']):
        """
        Args:
             directory_path (str): Path to directory containing Communications files
             comm_extensions (str[]): List of strings specifying filename extensions
                                         to be associated with Communications
        """
        self.comm_id_to_comm_path = {}

        logging.info("Caching names of files with extensions [%s] in '%s'" %
                     (', '.join(comm_extensions), directory_path))

        # Recursively traverse subdirectories
        for root, dirs, files in os.walk(directory_path):
            for basename in files:
                (comm_id, extension) = os.path.splitext(basename)
                if extension in comm_extensions:
                    comm_filename = os.path.join(root, basename)
                    self.comm_id_to_comm_path[comm_id] = comm_filename

        logging.info("Finished caching %d Communication filenames in '%s'" %
                     (len(self.comm_id_to_comm_path), directory_path))

    def __getitem__(self, communication_id):
        if communication_id in self.comm_id_to_comm_path:
            comm_path = self.comm_id_to_comm_path[communication_id]
            logging.info("Reading Communication with ID '%s'" % comm_path)
            if not os.path.exists(comm_path):
                logging.error("Unable to find file with path '%s'" % comm_path)
                raise KeyError
            if os.path.splitext(comm_path)[1] == '.gz':
                with gzip.open(comm_path) as gzip_file:
                    buf = gzip_file.read()
                    comm = read_communication_from_buffer(buf)
            else:
                comm = read_communication_from_file(comm_path)
            return comm
        else:
            logging.info('No Communication with ID: %s' % communication_id)
            raise KeyError

    def __iter__(self):
        return self.comm_id_to_comm_path.__iter__()

    def __len__(self):
        return len(self.comm_id_to_comm_path)


class FetchBackedCommunicationContainer(collections.Mapping):
    """Maps Comm IDs to Comms, retrieving Comms from a
    :mod:`.FetchCommunicationService` server

    `FetchBackedCommunicationContainer` instances behave as dict-like data
    structures that map Communication IDs to Communications.  Communications
    are lazily-retrieved from a :mod:`.FetchCommunicationService`.

    If you need to retrieve large amounts of data from a
    :mod:`.FetchCommunicationService`, then you SHOULD NOT USE THIS CLASS.
    This class retrieves one Communication at a time using
    :mod:`.FetchCommunicationService`.
    """

    def __init__(self, host, port):
        """
        Args:
            host (str): Hostname of :mod:`.FetchCommunicationService` server
            port (int): Port # of :mod:`.FetchCommunicationService` server
        """
        self.host = host
        self.port = port

    def __getitem__(self, communication_id):
        with FetchCommunicationClientWrapper(self.host, self.port) as fc:
            fetch_result = fc.fetch(FetchRequest(communicationIds=[communication_id]))
            total_results = len(fetch_result.communications)
            if total_results == 0:
                raise KeyError
            elif total_results == 1:
                return fetch_result.communications[0]
            else:
                raise Exception("FetchBackedCommunicationContainer.__get_item__() "
                                "expected to receive 1 Communication, but instead "
                                "received %d Communications" % total_results)

    def __iter__(self):
        with FetchCommunicationClientWrapper(self.host, self.port) as fc:
            n = fc.getCommunicationCount()
            return fc.getCommunicationIDs(0, n).__iter__()

    def __len__(self):
        with FetchCommunicationClientWrapper(self.host, self.port) as fc:
            return fc.getCommunicationCount()


class MemoryBackedCommunicationContainer(collections.Mapping):
    """Maps Comm IDs to Comms by loading all Comms in file into memory

    `FetchBackedCommunicationContainer` instances behave as dict-like
    data structures that map Communication IDs to Communications.  All
    Communications in `communications_file` will be read into memory
    using a :class:`.CommunicationReader` instance.
    """

    def __init__(self, communications_file, max_file_size=1073741824):
        """
        Args:
            communications_file (str): String specifying name of Communications file
            max_file_size (int): Maximum file size, in bytes
        """
        self.comm_id_to_comm = {}

        comm_file_size = os.path.getsize(communications_file)
        if comm_file_size > max_file_size:
            raise Exception(
                ("MemoryBackedComunicationContainer will not open the file "
                 "'%s' because the file's size (%s) is larger than the "
                 "maximum specified file size of %s.  If you would like to "
                 "read a file this large into memory, you will need to "
                 "specify a larger value for the 'max_file_size'parameter.") %
                (communications_file,
                 humanfriendly.format_size(comm_file_size, binary=True),
                 humanfriendly.format_size(max_file_size, binary=True)))

        logging.info("Reading in Communications from file '%s'" %
                     communications_file)
        logging.info("Communication IDs:")
        for (comm, _) in CommunicationReader(communications_file):
            self.comm_id_to_comm[comm.id] = comm
            logging.info("  %s" % comm.id)
        logging.info("Finished reading communications.\n")

    def __getitem__(self, communication_id):
        return self.comm_id_to_comm[communication_id]

    def __iter__(self):
        return self.comm_id_to_comm.__iter__()

    def __len__(self):
        return len(self.comm_id_to_comm)


class ZipFileBackedCommunicationContainer(collections.Mapping):
    """Maps Comm IDs to Comms, retrieving Comms from a Zip file

    `ZipFileBackedCommunicationContainer` instances behave as dict-like
    data structures that map Communication IDs to Communications.
    Communications are lazily-retrieved from a Zip file.
    """

    def __init__(self, zipfile_path, comm_extensions=['.comm', '.concrete']):
        """
        Args:
            zipfile_path (str): Path to Zip file containing Communications
            comm_extensions (str[]): List of strings specifying filename extensions
                                 associated with Communications
        """
        self.comm_id_to_filename = {}
        self.zipfile = zipfile.ZipFile(zipfile_path, 'r')
        for filename in self.zipfile.namelist():
            (comm_id, extension) = os.path.splitext(os.path.basename(filename))
            if extension in comm_extensions:
                self.comm_id_to_filename[comm_id] = filename

    def __exit__(self):
        self.zipfile.close()

    def __getitem__(self, communication_id):
        filename = self.comm_id_to_filename[communication_id]
        buf = self.zipfile.read(filename)
        comm = read_communication_from_buffer(buf)
        return comm

    def __iter__(self):
        return self.comm_id_to_filename.__iter__()

    def __len__(self):
        return len(self.comm_id_to_filename)


class RedisHashBackedCommunicationContainer(collections.Mapping):
    """Maps Comm IDs to Comms, retrieving Comms from a Redis hash

    `RedisHashBackedCommunicationContainer` instances behave as dict-like
    data structures that map Communication IDs to Communications.
    Communications are lazily-retrieved from a Redis hash.
    """

    def __init__(self, redis_db, key):
        """
        Args:
            redis_db (redis.Redis): redis database connection
            key (str): Key in redis database where hash is located
        """
        self.redis_db = redis_db
        self.key = key

    def __getitem__(self, communication_id):
        buf = self.redis_db.hget(self.key, communication_id)
        if buf is None:
            raise KeyError
        comm = read_communication_from_buffer(buf)
        return comm

    def __contains__(self, communication_id):
        return self.redis_db.hexists(self.key, communication_id)

    def __iter__(self):
        return iter(self.redis_db.hkeys(self.key))

    def __len__(self):
        return self.redis_db.hlen(self.key)
