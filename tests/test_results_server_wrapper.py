from __future__ import unicode_literals
import mock
from mock import sentinel
from pytest import fixture

from concrete.services.results import ResultsServerService
from concrete.util import (
    ResultsServerServiceWrapper, ResultsServerClientWrapper
)
from concrete.util import ThriftFactory


@fixture
def results_server_client_wrapper_triple():
    host = 'fake-host'
    port = 2
    return (host, port, ResultsServerClientWrapper(host, port))


@fixture
def results_server_service_wrapper():
    class Implementation(ResultsServerService.Iface):
        def regisiterSearchResult(self, result, taskType):
            raise NotImplementedError

        def getSearchResults(self, taskType, limit):
            raise NotImplementedError

        def getSearchResultsByUser(self, taskType, userId, limit):
            raise NotImplementedError

        def about(self):
            raise NotImplementedError

        def alive(self):
            raise NotImplementedError

    implementation = Implementation()

    return ResultsServerServiceWrapper(implementation)


@mock.patch('concrete.services.results.ResultsServerService.Client')
@mock.patch.object(ThriftFactory, 'createProtocol',
                   return_value=sentinel.protocol)
@mock.patch.object(ThriftFactory, 'createTransport')
@mock.patch.object(ThriftFactory, 'createSocket',
                   return_value=sentinel.socket)
def test_enter(mock_create_socket, mock_create_transport,
               mock_create_protocol, mock_client,
               results_server_client_wrapper_triple):
    (host, port,
        results_server_client_wrapper) = results_server_client_wrapper_triple

    # create additional mocks for transport.open call...
    mock_transport = mock.Mock()
    mock_create_transport.return_value = mock_transport
    # ...and to verify the instantiation of the
    # ResultsServerService.Client
    mock_client.return_value = sentinel.client

    client = results_server_client_wrapper.__enter__()
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


def test_exit(results_server_client_wrapper_triple):
    (host, port,
        results_server_client_wrapper) = results_server_client_wrapper_triple

    # create mock for transport.close call
    mock_transport = mock.Mock()
    results_server_client_wrapper.transport = mock_transport

    results_server_client_wrapper.__exit__(mock.ANY, mock.ANY, mock.ANY)

    # verify invocations
    mock_transport.close.assert_called_once_with()


@mock.patch.object(ThriftFactory, 'createServer')
def test_serve(mock_create_server, results_server_service_wrapper):
    # create mock for server.serve invocation
    mock_server = mock.Mock()
    mock_create_server.return_value = mock_server

    host = 'fake-host'
    port = 2

    results_server_service_wrapper.serve(host, port)

    # verify method invocations
    mock_create_server.assert_called_once_with(
        results_server_service_wrapper.processor, host, port)
    mock_server.serve.assert_called_once_with()
