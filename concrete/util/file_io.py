"""
"""

from thrift import TSerialization

from concrete import Communication, TokenLattice
from concrete.util.references import add_references_to_communication


def read_thrift_from_file(thrift_obj, filename):
    """
    Pass in a new thrift object and a filename. Read in bytes from disk that
    match that thrift object.

    Return the deserialized thrift object.
    """
    thrift_file = open(filename)
    thrift_bytes = thrift_file.read()
    TSerialization.deserialize(thrift_obj, thrift_bytes)
    thrift_file.close()
    return thrift_obj

def read_communication_from_file(communication_filename):
    """
    Takes the filename of a serialized Concrete Communication file,
    reads the Communication from the file and returns an instantiated
    Communication instance.
    """
    comm = read_thrift_from_file(Communication(), communication_filename)
    add_references_to_communication(comm)
    return comm

def read_tokenlattice_from_file(tokenlattice_filename):
    """
    Takes the filename of a serialized Concrete TokenLattice file,
    reads the TokenLattice from the file and returns an instantiated
    TokenLattice instance.
    """
    return read_thrift_from_file(TokenLattice(), tokenlattice_filename)

def write_communication_to_file(communication, communication_filename):
    return write_thrift_to_file(communication, communication_filename)

def write_thrift_to_file(thrift_obj, filename):
    thrift_bytes = TSerialization.serialize(thrift_obj)
    thrift_file = open(filename, "w")
    thrift_file.write(thrift_bytes)
    thrift_file.close()
