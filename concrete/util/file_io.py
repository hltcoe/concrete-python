"""
"""

from thrift import TSerialization

from concrete import Communication


def read_communication_from_file(communication_filename):
    """
    Takes the filename of a serialized Concrete Communication file,
    reads the Communication from the file and returns an instantiated
    Communication instance.
    """
    comm = Communication()
    comm_bytestring = open(communication_filename).read()
    TSerialization.deserialize(comm, comm_bytestring)
    return comm
