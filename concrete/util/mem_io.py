from __future__ import unicode_literals
from thrift.transport.TTransport import TMemoryBuffer

from .thrift_factory import factory
from .references import add_references_to_communication
from ..communication.ttypes import Communication


def read_communication_from_buffer(buf, add_references=True):
    '''
    Deserialize buf (a binary string) and return resulting
    communication.  Add references if requested.

    Args:
        buf (str): String representing communication encoded from thrift
        add_references (bool): If True, calls
           :func:`concrete.util.references.add_references_to_communication`
           on :class:`.Communication` read from buffer

    Returns:
        Communication: Communication read from buffer
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

    Args:
        comm (Communication): communication to serialize

    Returns:
        Communication: Communication read from buffer
    '''
    transport = TMemoryBuffer()
    protocol = factory.createProtocol(transport)
    comm.write(protocol)
    return transport.getvalue()


def communication_deep_copy(comm):
    '''
    Return deep copy of communication.

    Args:
        comm (Communication): communication to copy

    Returns:
        Communication: deep copy of comm
    '''
    return read_communication_from_buffer(
        write_communication_to_buffer(comm), add_references=False
    )
