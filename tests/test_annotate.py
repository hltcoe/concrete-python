from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.protocol import TCompactProtocol

import unittest

from concrete.util.annotate_wrapper import (
    SubprocessAnnotateCommunicationServiceWrapper
)
from concrete.util.net import find_port
from concrete.util.simple_comm import create_comm


from time import time

from concrete.annotate import AnnotateCommunicationService
from concrete.metadata.ttypes import AnnotationMetadata


class NoopAnnotateCommunicationService(AnnotateCommunicationService.Iface):
    METADATA_TOOL = 'No-op AnnotateCommunicationService'

    def annotate(self, communication):
        return communication

    def getMetadata(self,):
        metadata = AnnotationMetadata(tool=self.METADATA_TOOL,
                                      timestamp=int(time()))
        return metadata

    def getDocumentation(self):
        return '''\
        AnnotateCommunicationService that returns communication unmodified
        '''

    def shutdown(self):
        pass


class TestAnnotateCommunicationService(unittest.TestCase):

    def test_annotate(self):
        impl = NoopAnnotateCommunicationService()
        host = 'localhost'
        port = find_port()
        timeout = 5

        comm_id = '1-2-3-4'
        comm = create_comm(comm_id)

        comm_uuid_uuidString = comm.uuid.uuidString
        comm_metadata_tool = comm.metadata.tool
        comm_metadata_timestamp = comm.metadata.timestamp

        with SubprocessAnnotateCommunicationServiceWrapper(impl, host, port,
                                                           timeout=timeout):
            transport = TSocket.TSocket(host, port)
            transport = TTransport.TFramedTransport(transport)
            protocol = TCompactProtocol.TCompactProtocol(transport)

            cli = AnnotateCommunicationService.Client(protocol)
            transport.open()
            res = cli.annotate(comm)
            transport.close()

            self.assertEqual(res.id, comm_id)
            self.assertEqual(res.uuid.uuidString, comm_uuid_uuidString)
            self.assertEqual(res.metadata.tool, comm_metadata_tool)
            self.assertEqual(res.metadata.timestamp, comm_metadata_timestamp)

    def test_get_metadata(self):
        impl = NoopAnnotateCommunicationService()
        host = 'localhost'
        port = find_port()
        timeout = 5

        with SubprocessAnnotateCommunicationServiceWrapper(impl, host, port,
                                                           timeout=timeout):
            transport = TSocket.TSocket(host, port)
            transport = TTransport.TFramedTransport(transport)
            protocol = TCompactProtocol.TCompactProtocol(transport)

            cli = AnnotateCommunicationService.Client(protocol)
            transport.open()
            metadata = cli.getMetadata()
            transport.close()

            self.assertEqual(NoopAnnotateCommunicationService.METADATA_TOOL,
                             metadata.tool)
