from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TCompactProtocol
from thrift.server import TServer


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


factory = ThriftFactory(TTransport.TFramedTransportFactory(),
                        TCompactProtocol.TCompactProtocolFactory())
