import mock
from mock import sentinel
import unittest

from concrete.services import Annotator
from concrete.util import annotator_wrapper
from concrete.util.thrift_factory import ThriftFactory


class AnnotatorClientWrapperTest(unittest.TestCase):
    def setUp(self):
        self.host = 'fake-host'
        self.port = 'fake-port'

        self.wrapper = annotator_wrapper.AnnotatorClientWrapper(self.host,
                                                                self.port)

    @mock.patch('concrete.services.Annotator.Client')
    @mock.patch.object(ThriftFactory, 'createProtocol',
                       return_value=sentinel.protocol)
    @mock.patch.object(ThriftFactory, 'createTransport')
    @mock.patch.object(ThriftFactory, 'createSocket',
                       return_value=sentinel.socket)
    def test___enter__(self, mock_create_socket, mock_create_transport,
                       mock_create_protocol, mock_client):
        # create additional mocks for transport.open call...
        mock_transport = mock.Mock()
        mock_create_transport.return_value = mock_transport
        # ...and to verify the instantiation of the Annotator.Client
        mock_client.return_value = sentinel.client

        client = self.wrapper.__enter__()
        # check return value
        self.assertEquals(sentinel.client, client)

        # verify method invocations
        mock_create_socket.assert_called_once_with(self.host, self.port)
        mock_create_transport.assert_called_once_with(
            mock_create_socket.return_value)
        mock_create_protocol.assert_called_once_with(
            mock_create_transport.return_value)
        mock_client.assert_called_once_with(mock_create_protocol.return_value)

        mock_transport.open.assert_called_once_with()

    def test___exit__(self):
        # create mock for transport.close call
        mock_transport = mock.Mock()
        self.wrapper.transport = mock_transport

        self.wrapper.__exit__(mock.ANY, mock.ANY, mock.ANY)

        # verify invocations
        mock_transport.close.assert_called_once_with()


class AnnotatorServiceWrapperTest(unittest.TestCase):
    def setUp(self):
        class Implementation(Annotator.Iface):
            def annotate(communication):
                raise NotImplementedError

            def getMetadata():
                raise NotImplementedError

            def getDocumentation():
                raise NotImplementedError

            def shutdown():
                raise NotImplementedError

        implementation = Implementation()

        self.wrapper = \
            annotator_wrapper.AnnotatorServiceWrapper(implementation)

    @mock.patch.object(ThriftFactory, 'createServer')
    def test_serve(self, mock_create_server):
        # create mock for server.serve invocation
        mock_server = mock.Mock()
        mock_create_server.return_value = mock_server

        host = 'fake-host'
        port = 'fake-port'

        self.wrapper.serve(host, port)

        # verify method invocations
        mock_create_server.assert_called_once_with(self.wrapper.processor,
                                                   host, port)
        mock_server.serve.assert_called_once_with()
