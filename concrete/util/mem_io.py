from thrift.transport.TTransport import TMemoryBuffer

from concrete.util.thrift_factory import factory
from concrete.util.references import add_references_to_communication
from concrete import Communication


def read_communication_from_buffer(buf, add_references=True):
    '''
    Deserialize buf (a binary string) and return resulting
    communication.  Add references if requested.
    '''
    transport_in = TMemoryBuffer(buf)
    protocol_in = factory.createProtocol(transport_in)
    comm = Communication()
    comm.read(protocol_in)
    if add_references:
        add_references_to_communication(comm)
    return comm


def write_communication_to_buffer(comm):
    '''
    Serialize communication to buffer (binary string) and return
    buffer.
    '''
    transport = TMemoryBuffer()
    protocol = factory.createProtocol(transport)
    comm.write(protocol)
    return transport.getvalue()


def communication_deep_copy(comm):
    '''
    Return deep copy of communication.
    '''
    return read_communication_from_buffer(
        write_communication_to_buffer(comm), add_references=False
    )
