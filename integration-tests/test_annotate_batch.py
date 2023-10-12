from __future__ import unicode_literals
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.protocol import TCompactProtocol

from concrete.util import (
    SubprocessAnnotateCommunicationBatchServiceWrapper
)
from concrete.util import find_port
from concrete.util import create_comm


from time import time

from concrete.annotate import AnnotateCommunicationBatchService
from concrete import AnnotationMetadata


class NoopAnnotateCommunicationBatchService(AnnotateCommunicationBatchService.Iface):
    METADATA_TOOL = 'No-op AnnotateCommunicationBatchService'

    def annotate(self, communicationBatch):
        return [communication for communication in communicationBatch]

    def getMetadata(self,):
        metadata = AnnotationMetadata(tool=self.METADATA_TOOL,
                                      timestamp=int(time()))
        return metadata

    def getDocumentation(self):
        return '''\
        AnnotateCommunicationBatchService that returns communication unmodified
        '''

    def shutdown(self):
        pass


def test_annotate_batch():
    impl = NoopAnnotateCommunicationBatchService()
    host = '127.0.0.1'
    port = find_port()
    timeout = 5

    comm_1_id = '1-2-3-4'
    comm_1 = create_comm(comm_1_id)

    comm_1_uuid_uuidString = comm_1.uuid.uuidString
    comm_1_metadata_tool = comm_1.metadata.tool
    comm_1_metadata_timestamp = comm_1.metadata.timestamp

    comm_2_id = '5-6-7-8'
    comm_2 = create_comm(comm_2_id)

    comm_2_uuid_uuidString = comm_2.uuid.uuidString
    comm_2_metadata_tool = comm_2.metadata.tool
    comm_2_metadata_timestamp = comm_2.metadata.timestamp

    with SubprocessAnnotateCommunicationBatchServiceWrapper(impl, host, port,
                                                            timeout=timeout):
        transport = TSocket.TSocket(host, port)
        transport = TTransport.TFramedTransport(transport)
        protocol = TCompactProtocol.TCompactProtocolAccelerated(transport)

        cli = AnnotateCommunicationBatchService.Client(protocol)
        transport.open()
        res = cli.annotate([comm_1, comm_2])
        transport.close()

        assert len(res) == 2

        assert res[0].id == comm_1_id
        assert res[0].uuid.uuidString == comm_1_uuid_uuidString
        assert res[0].metadata.tool == comm_1_metadata_tool
        assert res[0].metadata.timestamp == comm_1_metadata_timestamp

        assert res[1].id == comm_2_id
        assert res[1].uuid.uuidString == comm_2_uuid_uuidString
        assert res[1].metadata.tool == comm_2_metadata_tool
        assert res[1].metadata.timestamp == comm_2_metadata_timestamp


def test_get_metadata():
    impl = NoopAnnotateCommunicationBatchService()
    host = '127.0.0.1'
    port = find_port()
    timeout = 5

    with SubprocessAnnotateCommunicationBatchServiceWrapper(impl, host, port,
                                                            timeout=timeout):
        transport = TSocket.TSocket(host, port)
        transport = TTransport.TFramedTransport(transport)
        protocol = TCompactProtocol.TCompactProtocolAccelerated(transport)

        cli = AnnotateCommunicationBatchService.Client(protocol)
        transport.open()
        metadata = cli.getMetadata()
        transport.close()

        assert NoopAnnotateCommunicationBatchService.METADATA_TOOL == metadata.tool
