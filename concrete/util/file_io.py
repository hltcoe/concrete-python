"""
"""

import gzip
import mimetypes
import os.path
import tarfile
import zipfile

from thrift import TSerialization
from thrift.protocol import TCompactProtocol
from thrift.transport import TTransport

from concrete import Communication, TokenLattice
from concrete.util.references import add_references_to_communication


def read_thrift_from_file(thrift_obj, filename):
    """Instantiate Thrift object from contents of named file

    The Thrift file is assumed to be encoded using TCompactProtocol

    WARNING - Thrift deserialization tends to fail silently.  For
    example, the Thrift libraries will not complain if you try to
    deserialize data from the file '/dev/urandom'.

    Args:
        thrift_obj: A Thrift object (e.g. a Communication object)
        filename:  A filename string

    Returns:
        The Thrift object that was passed in as an argument
    """
    thrift_file = open(filename, "rb")
    thrift_bytes = thrift_file.read()
    TSerialization.deserialize(thrift_obj, thrift_bytes, protocol_factory=TCompactProtocol.TCompactProtocolFactory())
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
    thrift_bytes = TSerialization.serialize(thrift_obj, protocol_factory=TCompactProtocol.TCompactProtocolFactory())
    thrift_file = open(filename, "wb")
    thrift_file.write(thrift_bytes)
    thrift_file.close()


class CommunicationReader:
    """Class for reading one or more Communications from a file

    Support filetypes are:
    - a file with a single Communication
    - a file with multiple Communications concatenated together
    - a gzipped file with a single Communication
    - a gzipped file with multiple Communications concatenated together
    - a .tar.gz file with one or more Communications
    - a .zip file with one or more Communications
    """
    def __init__(self, filename):
        if tarfile.is_tarfile(filename):
            # File is either a '.tar' or '.tar.gz' file
            self.filetype = 'tar'
            self.tar = tarfile.open(filename)
        elif zipfile.is_zipfile(filename):
            self.filetype = 'zip'
            self.zip = zipfile.ZipFile(filename, 'r')
            self.zip_infolist = self.zip.infolist()
            self.zip_infolist_index = 0
        elif mimetypes.guess_type(filename)[1] == 'gzip':
            self.filetype = 'stream'
            f = gzip.open(filename, 'rb')
        else:
            self.filetype = 'stream'
            f = open(filename, 'rb')

        if self.filetype is 'stream':
            self.transport = TTransport.TFileObjectTransport(f)
            self.protocol = TCompactProtocol.TCompactProtocol(self.transport)
            self.transport.open()

    def __iter__(self):
        return self

    def next(self):
        if self.filetype is 'stream':
            return self.next_from_stream()
        elif self.filetype is 'tar':
            return self.next_from_tar()
        elif self.filetype is 'zip':
            return self.next_from_zip()

    def next_from_stream(self):
        try:
            comm = Communication()
            comm.read(self.protocol)
            add_references_to_communication(comm)
            return comm
        except EOFError:
            self.transport.close()
            raise StopIteration

    def next_from_tar(self):
        while True:
            tarinfo = self.tar.next()
            if tarinfo is None:
                raise StopIteration
            if not tarinfo.isfile():
                # Ignore directories
                continue
            filename = os.path.split(tarinfo.name)[-1]
            if filename[0] is '.' and filename[1] is '_':
                # Ignore attribute files created by OS X tar
                continue
            comm = TSerialization.deserialize(
                Communication(),
                self.tar.extractfile(tarinfo).read(),
                protocol_factory=TCompactProtocol.TCompactProtocolFactory())
            add_references_to_communication(comm)
            return comm

    def next_from_zip(self):
        if self.zip_infolist_index >= len(self.zip_infolist):
            raise StopIteration
        zipinfo = self.zip_infolist[self.zip_infolist_index]
        self.zip_infolist_index += 1
        comm = TSerialization.deserialize(
            Communication(),
            self.zip.open(zipinfo).read(),
            protocol_factory=TCompactProtocol.TCompactProtocolFactory())
        add_references_to_communication(comm)
        return comm
