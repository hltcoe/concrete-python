import mock
from mock import sentinel
from pytest import fixture

from concrete.services import Annotator
from concrete.util.annotator_wrapper import (
    AnnotatorServiceWrapper, AnnotatorClientWrapper
)
from concrete.util.thrift_factory import ThriftFactory


@fixture
def annotator_client_wrapper_triple():
    host = 'fake-host'
    port = 'fake-port'
    return (host, port, AnnotatorClientWrapper(host, port))


@fixture
def annotator_service_wrapper():
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

    return AnnotatorServiceWrapper(implementation)


@mock.patch('concrete.services.Annotator.Client')
@mock.patch.object(ThriftFactory, 'createProtocol',
                   return_value=sentinel.protocol)
@mock.patch.object(ThriftFactory, 'createTransport')
@mock.patch.object(ThriftFactory, 'createSocket',
                   return_value=sentinel.socket)
def test_enter(mock_create_socket, mock_create_transport,
               mock_create_protocol, mock_client,
               annotator_client_wrapper_triple):
    (host, port, annotator_client_wrapper) = annotator_client_wrapper_triple

    # create additional mocks for transport.open call...
    mock_transport = mock.Mock()
    mock_create_transport.return_value = mock_transport
    # ...and to verify the instantiation of the Annotator.Client
    mock_client.return_value = sentinel.client

    client = annotator_client_wrapper.__enter__()
    # check return value
    assert sentinel.client == client

    # verify method invocations
    mock_create_socket.assert_called_once_with(host, port)
    mock_create_transport.assert_called_once_with(
        mock_create_socket.return_value)
    mock_create_protocol.assert_called_once_with(
        mock_create_transport.return_value)
    mock_client.assert_called_once_with(mock_create_protocol.return_value)

    mock_transport.open.assert_called_once_with()


def test_exit(annotator_client_wrapper_triple):
    (host, port, annotator_client_wrapper) = annotator_client_wrapper_triple

    # create mock for transport.close call
    mock_transport = mock.Mock()
    annotator_client_wrapper.transport = mock_transport

    annotator_client_wrapper.__exit__(mock.ANY, mock.ANY, mock.ANY)

    # verify invocations
    mock_transport.close.assert_called_once_with()


@mock.patch.object(ThriftFactory, 'createServer')
def test_serve(mock_create_server, annotator_service_wrapper):
    # create mock for server.serve invocation
    mock_server = mock.Mock()
    mock_create_server.return_value = mock_server

    host = 'fake-host'
    port = 'fake-port'

    annotator_service_wrapper.serve(host, port)

    # verify method invocations
    mock_create_server.assert_called_once_with(
        annotator_service_wrapper.processor, host, port)
    mock_server.serve.assert_called_once_with()
