from concrete.access import FetchCommunicationService
from concrete.util.thrift_factory import factory


class ConcreteServiceClientWrapper(object):
    def __init__(self, host, port):
        if not hasattr(self, 'concrete_service_class'):
            raise NotImplementedError(
                "Child classes of ConcreteServiceWrapper must set the " +
                "'concrete_service_factory' attribute to a class that " +
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


FetchCommunicationClientWrapper = type(
    'FetchCommunicationClientWrapper',
    (ConcreteServiceClientWrapper,),
    {'concrete_service_class': FetchCommunicationService})
