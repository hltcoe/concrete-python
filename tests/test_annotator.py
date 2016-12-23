from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.protocol import TCompactProtocol

import unittest

from concrete.util.annotator_wrapper import SubprocessAnnotatorServiceWrapper
from concrete.util.net import find_port
from concrete.util.simple_comm import create_comm


from time import time

from concrete.services import Annotator
from concrete.metadata.ttypes import AnnotationMetadata


class NoopAnnotator(Annotator.Iface):
    METADATA_TOOL = 'No-op Annotator'

    def annotate(self, communication):
        return communication

    def getMetadata(self,):
        metadata = AnnotationMetadata(tool=self.METADATA_TOOL,
                                      timestamp=int(time()))
        return metadata

    def getDocumentation(self):
        return 'Annotator that returns communication unmodified'

    def shutdown(self):
        pass


class TestAnnotator(unittest.TestCase):

    def test_annotate(self):
        impl = NoopAnnotator()
        host = 'localhost'
        port = find_port()
        timeout = 5

        comm_id = '1-2-3-4'
        comm = create_comm(comm_id)

        comm_uuid_uuidString = comm.uuid.uuidString
        comm_metadata_tool = comm.metadata.tool
        comm_metadata_timestamp = comm.metadata.timestamp

        with SubprocessAnnotatorServiceWrapper(impl, host, port,
                                               timeout=timeout):
            transport = TSocket.TSocket(host, port)
            transport = TTransport.TFramedTransport(transport)
            protocol = TCompactProtocol.TCompactProtocol(transport)

            cli = Annotator.Client(protocol)
            transport.open()
            res = cli.annotate(comm)
            transport.close()

            self.assertEqual(res.id, comm_id)
            self.assertEqual(res.uuid.uuidString, comm_uuid_uuidString)
            self.assertEqual(res.metadata.tool, comm_metadata_tool)
            self.assertEqual(res.metadata.timestamp, comm_metadata_timestamp)

    def test_get_metadata(self):
        impl = NoopAnnotator()
        host = 'localhost'
        port = find_port()
        timeout = 5

        with SubprocessAnnotatorServiceWrapper(impl, host, port,
                                               timeout=timeout):
            transport = TSocket.TSocket(host, port)
            transport = TTransport.TFramedTransport(transport)
            protocol = TCompactProtocol.TCompactProtocol(transport)

            cli = Annotator.Client(protocol)
            transport.open()
            metadata = cli.getMetadata()
            transport.close()

            self.assertEqual(NoopAnnotator.METADATA_TOOL, metadata.tool)
