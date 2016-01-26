from thrift.transport.TTransport import TMemoryBuffer

from concrete.util import thrift_factory as thrift
from concrete.util.references import add_references_to_communication
from concrete import Communication


def read_communication_from_buffer(buf, add_references=True):
    '''
    Deserialize buf and return resulting communication.
    Add references if requested.
    '''
    transport_in = TMemoryBuffer(buf)
    protocol_in = thrift.factory.createProtocol(transport_in)
    comm = Communication()
    comm.read(protocol_in)
    if add_references:
        add_references_to_communication(comm)
    return comm


def write_communication_to_buffer(comm):
    '''
    Serialize communication and return result.
    '''
    transport = TMemoryBuffer()
    protocol = thrift.factory.createProtocol(transport)
    comm.write(protocol)
    return transport.getvalue()


def communication_deep_copy(comm):
    '''
    Return deep copy of communication.
    '''
    return read_communication_from_buffer(
        write_communication_to_buffer(comm), add_references=False
    )
