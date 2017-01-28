from __future__ import unicode_literals
from multiprocessing import Process
from time import sleep
from socket import create_connection

from .thrift_factory import factory


class ConcreteServiceClientWrapper(object):
    def __init__(self, host, port):
        if not hasattr(self, 'concrete_service_class'):
            raise NotImplementedError(
                "Child classes of ConcreteServiceClientWrapper must set " +
                "the 'concrete_service_class' attribute to a class that " +
                "implements a Concrete Service")

        self.host = host
        try:
            self.port = int(port)
        except ValueError:
            raise ValueError(
                "Service expected 'port' to be an integer, but it was '%s'" %
                port)

    def __enter__(self):
        socket = factory.createSocket(self.host, self.port)
        self.transport = factory.createTransport(socket)
        protocol = factory.createProtocol(self.transport)

        cli = self.concrete_service_class.Client(protocol)

        self.transport.open()
        return cli

    def __exit__(self, type, value, traceback):
        self.transport.close()


class ConcreteServiceWrapper(object):
    """
    A sample wrapper around a Concrete service.
    """

    def __init__(self, implementation):
        if not hasattr(self, 'concrete_service_class'):
            raise NotImplementedError(
                "Child classes of ConcreteServiceWrapper must set " +
                "the 'concrete_service_class' attribute to a class that " +
                "implements a Concrete Service")

        self.processor = self.concrete_service_class.Processor(implementation)

    def serve(self, host, port):
        server = factory.createServer(self.processor, host, port)

        # NOTE: Thrift's servers run indefinitely. This server implementation
        # may be killed by a KeyboardInterrupt (Control-C); otherwise, the
        # process must be killed to terminate the server.
        server.serve()


class SubprocessConcreteServiceWrapper(object):
    """
    Concrete Service wrapper that runs server in a subprocess via a
    context manager interface.
    """

    SLEEP_INTERVAL = 0.1

    def __init__(self, implementation, host, port, timeout=None):
        if not hasattr(self, 'concrete_service_wrapper_class'):
            raise NotImplementedError(
                "Child classes of SubprocessConcreteServiceWrapper must " +
                "set the 'concrete_service_wrapper_class' attribute to a " +
                "child class of ConcreteServiceWrapper")

        self.proc = None
        self.server = self.concrete_service_wrapper_class(implementation)
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
