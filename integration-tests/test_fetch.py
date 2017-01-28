from __future__ import unicode_literals
from concrete.util import (
    CommunicationContainerFetchHandler,
    RelayFetchHandler)
from concrete.util import (
    FetchCommunicationClientWrapper,
    SubprocessFetchCommunicationServiceWrapper)
from concrete.util import FetchBackedCommunicationContainer
from concrete.util import find_port
from concrete.util import create_comm
from concrete.validate import validate_communication


def test_comm_container_fetch_handler():
    comm_container = {
        'one': create_comm('one'),
        'two': create_comm('two')
    }

    impl = CommunicationContainerFetchHandler(comm_container)
    host = 'localhost'
    port = find_port()

    with SubprocessFetchCommunicationServiceWrapper(impl, host, port):
        with FetchCommunicationClientWrapper(host, port) as cli:
            assert cli.getCommunicationCount()
            ids = cli.getCommunicationIDs(0, 10)
            assert 'one' in ids
            assert 'two' in ids
            assert 'foo' not in ids


def test_fetch_backed_container():
    comm_container = {
        'one': create_comm('one'),
        'two': create_comm('two')
    }

    impl = CommunicationContainerFetchHandler(comm_container)
    host = 'localhost'
    port = find_port()

    with SubprocessFetchCommunicationServiceWrapper(impl, host, port):
        cc = FetchBackedCommunicationContainer(host, port)
        assert len(cc) == 2
        assert 'one' in cc
        assert 'two' in cc
        for comm_id in cc:
            comm = cc[comm_id]
            assert validate_communication(comm)


def test_relay_container_fetch_handler():
    comm_container = {
        'one': create_comm('one'),
        'two': create_comm('two')
    }

    impl = CommunicationContainerFetchHandler(comm_container)
    host = 'localhost'
    port = find_port()

    with SubprocessFetchCommunicationServiceWrapper(impl, host, port):
        relay_impl = RelayFetchHandler(host, port)
        relay_host = 'localhost'
        relay_port = find_port()

        with SubprocessFetchCommunicationServiceWrapper(relay_impl, relay_host, relay_port):
            with FetchCommunicationClientWrapper(relay_host, relay_port) as cli:
                assert cli.getCommunicationCount()
                ids = cli.getCommunicationIDs(0, 10)
                assert 'one' in ids
                assert 'two' in ids
                assert 'foo' not in ids
