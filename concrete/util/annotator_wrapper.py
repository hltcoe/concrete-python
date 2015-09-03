from thrift import Thrift, TSerialization
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TCompactProtocol
from thrift.server import TServer

from concrete.services import *
from concrete.services.ttypes import *

import time

class AnnotatorClientWrapper:
    """
    A sample client implementation of the Concrete Annotator service.

    Provides sensible/current defaults for transport and protocol.

    TODO: named args for transport/protocol?
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = TSocket.TSocket(self.host, self.port)
        self.transport = TTransport.TFramedTransport(self.sock)
        self.protocol = TCompactProtocol.TCompactProtocol(self.transport)
        self.cli = Annotator.Client(protocol)

        self.transport.open()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.transport.close()

    def annotate(self, comm):
        """
        Tiny wrapper around Annotator.annotate(Communication).
        """
        try:
            return self.cli.annotate(comm)
        except Thrift.TException, tx:
            print "Got an error: %s : perhaps the server isn't running there?" % (tx.message)

class AnnotatorServiceImpl:
    """
    Example implementation of the Concrete Annotator service.
    """
    def annotate(this, comm):
        comm.text = "haha"
        return comm

    def getMetadata(this):
        md = AnnotationMetadata()
        md.tool = "Sample service impl"
        md.timestamp = int(time.time())
        return md

    def getDocumentation(this):
        return "nothing"

    def shutdown(this):
        # no-op
        pass

class AnnotatorServiceWrapper:
    """
    A sample wrapper around the Concrete annotator
    service, providing an easy way to wrap an implementation
    of the Annotator service.
    """
    def __init__(self, impl, host, port):
        self.proc = Annotator.Processor(impl)
        self.sock = TSocket.TServerSocket(host, port)
        self.trans = TTransport.TFramedTransport(sock)
        self.proto = TCompactProtocol.TCompactProtocol(trans)
        self.srv = TServer.TThreadedServer(processor, sock, trans, proto)

        print "Server starting."
        srv.serve()

    def close(self):
        srv.stop();
