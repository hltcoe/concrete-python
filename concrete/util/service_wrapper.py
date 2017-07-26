from __future__ import unicode_literals
from multiprocessing import Process
from time import sleep
from socket import create_connection

from .thrift_factory import factory


class ConcreteServiceClientWrapper(object):
    '''
    Base class for a wrapper around a Concrete service client.
    Implements the context manager interface so client can be controlled
    using the `with:` statement (client connection is closed when the
    `with:` scope is exited).
    '''
    def __init__(self, host, port):
        '''
        Args:
            host (str): hostname to connect to
            port (int): port number to connect to
        '''
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
        '''
        Create and open connection.
        '''
        socket = factory.createSocket(self.host, self.port)
        self.transport = factory.createTransport(socket)
        protocol = factory.createProtocol(self.transport)

        cli = self.concrete_service_class.Client(protocol)

        self.transport.open()
        return cli

    def __exit__(self, type, value, traceback):
        '''
        Close connection.
        '''
        self.transport.close()


class ConcreteServiceWrapper(object):
    """
    Base class for a wrapper around a Concrete service that runs in
    (blocks) the current process.
    """

    def __init__(self, implementation):
        '''
        Args:
            implementation (object): handler of specified concrete
                service
        '''
        if not hasattr(self, 'concrete_service_class'):
            raise NotImplementedError(
                "Child classes of ConcreteServiceWrapper must set " +
                "the 'concrete_service_class' attribute to a class that " +
                "implements a Concrete Service")

        self.processor = self.concrete_service_class.Processor(implementation)

    def serve(self, host, port):
        '''
        Serve on specified host and port in current process, blocking
        until server is killed.  (If server is not killed by signal or
        otherwise it will block forever.)

        Args:
            host (str): hostname to serve on
            port (int): port number to serve on
        '''
        server = factory.createServer(self.processor, host, port)

        server.serve()


class SubprocessConcreteServiceWrapper(object):
    """
    Base class for a wrapper around a Concrete service that runs in
    a subprocess; implements the context manager interface so subprocess
    can be controlled using the `with:` statement (subprocess is stopped
    and joined when the `with:` scope is exited).
    """

    SLEEP_INTERVAL = 0.1

    def __init__(self, implementation, host, port, timeout=None):
        '''
        Args:
            implementation (object): handler of specified concrete
                service
            host (str): hostname that will be served on
                when context is entered
            port (int): port number that will be served on
                when context is entered
            timeout (int): number of seconds to wait for server to start
                in subprocess, when context is entered (if None, wait
                forever)
        '''
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
        '''
        Create and start subprocess.
        '''
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

                sleep(self.SLEEP_INTERVAL)
                elapsed += self.SLEEP_INTERVAL

        return self

    def __exit__(self, type, value, traceback):
        '''
        Stop and join subprocess.
        '''
        self.proc.terminate()
        self.proc.join()
