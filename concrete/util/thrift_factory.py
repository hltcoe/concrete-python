from __future__ import unicode_literals
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
        '''
        Return new thrift socket.

        Args:
            host (str): hostname to create socket on
            port (int): port number to create socket on

        Returns:
            :class:`TSocket.TSocket`
        '''
        socket = TSocket.TSocket(host, port)
        return socket

    def createTransport(self, socket):
        '''
        Return new thrift transport on socket..

        Args:
            socket (TSocket.TSocket): socket to create transport on

        Returns:
            :class:`TSocket.TSocket`
        '''
        transport = self.transportFactory.getTransport(socket)
        return transport

    def createProtocol(self, transport):
        '''
        Return new thrift protocol on transport.

        Args:
            transport (TTransport.TTransport): transport to create
                protocol on

        Returns:
            :class:`TTransport.TTransport`
        '''
        protocol = self.protocolFactory.getProtocol(transport)
        return protocol

    def createServer(self, processor, host, port):
        '''
        Return new thrift server given a service handler and the
        server host and port.

        Args:
            processor: concrete service handler
            host (str): hostname to serve on
            port (int): port number to serve on

        Returns:
            :class:`TServer.TThreadedServer`
        '''
        socket = TSocket.TServerSocket(host, port)

        server = TServer.TThreadedServer(processor, socket,
                                         self.transportFactory,
                                         self.protocolFactory)
        return server


factory = ThriftFactory(TTransport.TFramedTransportFactory(),
                        TCompactProtocol.TCompactProtocolAcceleratedFactory())


def is_accelerated():
    '''
    Return whether this concrete-python installation has accelerated
    serialization.

    Returns:
        True if this concrete-python installation is accelerated, False
        otherwise
    '''
    try:
        transport = TTransport.TMemoryBuffer()
        TCompactProtocol.TCompactProtocolAccelerated(transport, fallback=False)
        return True
    except:
        return False
