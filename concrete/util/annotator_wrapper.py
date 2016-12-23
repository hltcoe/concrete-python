from multiprocessing import Process
from time import sleep
from socket import create_connection

from concrete.services import Annotator
from concrete.util.thrift_factory import factory


class AnnotatorClientWrapper(object):
    """
    A sample client implementation of the Concrete Annotator service.

    Provides sensible/current defaults for transport and protocol.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __enter__(self):
        socket = factory.createSocket(self.host, self.port)
        self.transport = factory.createTransport(socket)
        protocol = factory.createProtocol(self.transport)

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

    def serve(self, host, port):
        server = factory.createServer(self.processor, host, port)

        # NOTE: Thrift's servers run indefinitely. This server implementation
        # may be killed by a KeyboardInterrupt (Control-C); otherwise, the
        # process must be killed to terminate the server.
        server.serve()


class SubprocessAnnotatorServiceWrapper(object):
    '''
    Annotator service wrapper that runs server in a subprocess via a
    context manager interface.
    '''

    SLEEP_INTERVAL = 0.1

    def __init__(self, implementation, host, port, timeout=None):
        self.proc = None
        self.server = AnnotatorServiceWrapper(implementation)
        self.host = host
        self.port = port
        self.timeout = timeout

    def __enter__(self):
        self.proc = Process(target=self.server.serve,
                            args=(self.host, self.port))
        self.proc.start()

        s = None
        elapsed = 0.

        # Loop until successful connect or timeout
        while s is None and (self.timeout is None or elapsed < self.timeout):
            try:
                s = create_connection((self.host, self.port))
                s.close()
            except:
                s = None

                # this is not precise... not important
                sleep(self.SLEEP_INTERVAL)
                elapsed += self.SLEEP_INTERVAL

        return self

    def __exit__(self, type, value, traceback):
        self.proc.terminate()
        self.proc.join()
