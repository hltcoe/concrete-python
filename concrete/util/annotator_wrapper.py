import time

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TCompactProtocol
from thrift.server import TServer

from concrete.metadata.ttypes import AnnotationMetadata
from concrete.services import Annotator


class AnnotatorClientWrapper(object):
    """
    A sample client implementation of the Concrete Annotator service.

    Provides sensible/current defaults for transport and protocol.

    TODO: named args for transport/protocol?
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __enter__(self):
        sock = TSocket.TSocket(self.host, self.port)
        self.transport = TTransport.TFramedTransport(sock)
        protocol = TCompactProtocol.TCompactProtocol(self.transport)

        cli = Annotator.Client(protocol)

        self.transport.open()
        return cli

    def __exit__(self, type, value, traceback):
        self.transport.close()


class AnnotatorServiceImpl(object):
    """
    Example implementation of the Concrete Annotator service.
    """

    def annotate(self, comm):
        comm.text = "haha"
        return comm

    def getMetadata(self):
        md = AnnotationMetadata()
        md.tool = "Sample service impl"
        md.timestamp = int(time.time())
        return md

    def getDocumentation(self):
        return "nothing"

    def shutdown(self):
        pass


class AnnotatorServiceWrapper(object):
    """
    A sample wrapper around the Concrete annotator
    service, providing an easy way to wrap an implementation
    of the Annotator service.
    """

    def __init__(self, implementation):
        self.processor = Annotator.Processor(implementation)

    def serve(self, host='localhost', port=33222):
        socket = TSocket.TServerSocket(host, port)
        transportFactory = TTransport.TFramedTransportFactory()
        protocolFactory = TCompactProtocol.TCompactProtocolFactory()
        server = TServer.TThreadedServer(self.processor, socket,
                                         transportFactory, protocolFactory)

        # NOTE: Thrift's servers run indefinitely. This server implementation
        # may be killed by a KeyboardInterrupt (Control-C); otherwise, the
        # process must be killed to terminate the server.
        server.serve()
