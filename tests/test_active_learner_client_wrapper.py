from __future__ import unicode_literals
import mock
from mock import sentinel
from pytest import fixture

from concrete.learn import ActiveLearnerClientService
from concrete.util import (
    ActiveLearnerClientServiceWrapper, ActiveLearnerClientClientWrapper
)
from concrete.util import ThriftFactory


@fixture
def learner_client_client_wrapper_triple():
    host = 'fake-host'
    port = 2
    return (host, port, ActiveLearnerClientClientWrapper(host, port))


@fixture
def learner_client_service_wrapper():
    class Implementation(ActiveLearnerClientService.Iface):
        def start(self, sessionId, task, contact):
            raise NotImplementedError

        def stop(self, sessionId):
            raise NotImplementedError

        def addAnnotations(self, sessionId, annotations):
            raise NotImplementedError

        def about(self):
            raise NotImplementedError

        def alive(self):
            raise NotImplementedError

    implementation = Implementation()

    return ActiveLearnerClientServiceWrapper(implementation)


@mock.patch('concrete.learn.ActiveLearnerClientService.Client')
@mock.patch.object(ThriftFactory, 'createProtocol',
                   return_value=sentinel.protocol)
@mock.patch.object(ThriftFactory, 'createTransport')
@mock.patch.object(ThriftFactory, 'createSocket',
                   return_value=sentinel.socket)
def test_enter(mock_create_socket, mock_create_transport,
               mock_create_protocol, mock_client,
               learner_client_client_wrapper_triple):
    (host, port,
        learner_client_client_wrapper) = learner_client_client_wrapper_triple

    # create additional mocks for transport.open call...
    mock_transport = mock.Mock()
    mock_create_transport.return_value = mock_transport
    # ...and to verify the instantiation of the
    # ActiveLearnerClientService.Client
    mock_client.return_value = sentinel.client

    client = learner_client_client_wrapper.__enter__()
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


def test_exit(learner_client_client_wrapper_triple):
    (host, port,
        learner_client_client_wrapper) = learner_client_client_wrapper_triple

    # create mock for transport.close call
    mock_transport = mock.Mock()
    learner_client_client_wrapper.transport = mock_transport

    learner_client_client_wrapper.__exit__(mock.ANY, mock.ANY, mock.ANY)

    # verify invocations
    mock_transport.close.assert_called_once_with()


@mock.patch.object(ThriftFactory, 'createServer')
def test_serve(mock_create_server, learner_client_service_wrapper):
    # create mock for server.serve invocation
    mock_server = mock.Mock()
    mock_create_server.return_value = mock_server

    host = 'fake-host'
    port = 2

    learner_client_service_wrapper.serve(host, port)

    # verify method invocations
    mock_create_server.assert_called_once_with(
        learner_client_service_wrapper.processor, host, port)
    mock_server.serve.assert_called_once_with()
