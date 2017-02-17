from __future__ import unicode_literals
import logging
import os

from ..access.ttypes import FetchResult
from ..services.ttypes import ServiceInfo
from .access_wrapper import FetchCommunicationClientWrapper
from .file_io import write_communication_to_file
from ..version import concrete_library_version


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
        logging.info("Received about() call")
        service_info = ServiceInfo()
        service_info.name = 'CommunicationContainerFetchHandler - %s' % \
                            type(self.communication_container)
        service_info.version = concrete_library_version()
        return service_info

    def alive(self):
        logging.info("Received alive() call")
        return True

    def fetch(self, fetch_request):
        logging.info("Received FetchRequest: %s" % fetch_request)
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
        logging.info('Received getCommunicationCount()')
        communicationCount = len(self.communication_container)
        logging.info('- Communication Count: %d' % communicationCount)
        return communicationCount

    def getCommunicationIDs(self, offset, count):
        logging.info('Received getCommunicationIDs() call')
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
        logging.info("DirectoryBackedStoreHandler.about() called")
        service_info = ServiceInfo()
        service_info.name = 'DirectoryBackedStoreHandler'
        service_info.version = concrete_library_version()
        return service_info

    def alive(self):
        logging.info("DirectoryBackedStoreHandler.alive() called")
        return True

    def store(self, communication):
        """Save Communication to a directory

        Stored Communication files will be named `[COMMUNICATION_ID].comm`.
        If a file with that name already exists, it will be overwritten.
        """
        logging.info(
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
        logging.info('RelayFetchHandler.about()')
        with FetchCommunicationClientWrapper(self.host, self.port) as fc:
            return fc.about()

    def alive(self):
        logging.info('RelayFetchHandler.alive()')
        with FetchCommunicationClientWrapper(self.host, self.port) as fc:
            return fc.alive()

    def fetch(self, request):
        logging.info('RelayFetchHandler.fetch()')
        with FetchCommunicationClientWrapper(self.host, self.port) as fc:
            return fc.fetch(request)

    def getCommunicationCount(self):
        logging.info('RelayFetchHandler.getCommunicationCount()')
        with FetchCommunicationClientWrapper(self.host, self.port) as fc:
            return fc.getCommunicationCount()

    def getCommunicationIDs(self, offset, count):
        logging.info('RelayFetchHandler.getCommunicationIDs(offset=%d, count=%d)' %
                     (offset, count))
        with FetchCommunicationClientWrapper(self.host, self.port) as fc:
            return fc.getCommunicationIDs(offset, count)
