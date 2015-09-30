from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TCompactProtocol
from thrift.server import TServer

from concrete.services import Annotator


class ThriftFactory(object):
    """Abstract factory to create Thrift objects for client and server."""

    def __init__(self, transportFactory, protocolFactory):
        self.transportFactory = transportFactory
        self.protocolFactory = protocolFactory

    def createSocket(self, host, port):
        socket = TSocket.TSocket(host, port)
        return socket

    def createTransport(self, socket):
        transport = self.transportFactory.getTransport(socket)
        return transport

    def createProtocol(self, transport):
        protocol = self.protocolFactory.getProtocol(transport)
        return protocol

    def createServer(self, processor, host, port):
        socket = TSocket.TServerSocket(host, port)

        server = TServer.TThreadedServer(processor, socket,
                                         self.transportFactory,
                                         self.protocolFactory)
        return server


thriftFactory = ThriftFactory(TTransport.TFramedTransportFactory(),
                              TCompactProtocol.TCompactProtocolFactory())


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
        socket = thriftFactory.createSocket(self.host, self.port)
        self.transport = thriftFactory.createTransport(socket)
        protocol = thriftFactory.createProtocol(self.transport)

        cli = Annotator.Client(protocol)

        self.transport.open()
        return cli

    def __exit__(self, type, value, traceback):
        self.transport.close()


class AnnotatorServiceWrapper(object):
    """
    A sample wrapper around the Concrete annotator
    service, providing an easy way to wrap an implementation
    of the Annotator service.
    """

    def __init__(self, implementation):
        self.processor = Annotator.Processor(implementation)

    def serve(self, host='localhost', port=33222):
        server = thriftFactory.createServer(self.processor, host, port)

        # NOTE: Thrift's servers run indefinitely. This server implementation
        # may be killed by a KeyboardInterrupt (Control-C); otherwise, the
        # process must be killed to terminate the server.
        server.serve()
