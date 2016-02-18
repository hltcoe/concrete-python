"""Code for reading and writing Concrete Communications
"""

import cStringIO
import gzip
import bz2
import mimetypes
import os.path
import tarfile
import zipfile

import os
import pwd
import grp
import time

from thrift import TSerialization
from thrift.transport import TTransport

from concrete import Communication, TokenLattice
from concrete.util.references import add_references_to_communication
from concrete.util.thrift_factory import factory


def read_thrift_from_file(thrift_obj, filename):
    """Instantiate Thrift object from contents of named file

    The Thrift file is assumed to be encoded using TCompactProtocol

    **WARNING** - Thrift deserialization tends to fail silently.  For
    example, the Thrift libraries will not complain if you try to
    deserialize data from the file `/dev/urandom`.

    Args:

    - `thrift_obj`: A Thrift object (e.g. a Communication object)
    - `filename`:  A filename string

    Returns:

    -  The Thrift object that was passed in as an argument
    """
    thrift_file = open(filename, "rb")
    thrift_bytes = thrift_file.read()
    TSerialization.deserialize(
        thrift_obj, thrift_bytes,
        protocol_factory=factory.protocolFactory)
    thrift_file.close()
    return thrift_obj


def read_communication_from_file(communication_filename, add_references=True):
    """Read a Communication from the file specified by filename

    Args:

    - `communication_filename`: String with filename

    Returns:

    - A Concrete `Communication` object
    """
    comm = read_thrift_from_file(Communication(), communication_filename)
    if add_references:
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
    thrift_bytes = TSerialization.serialize(
        thrift_obj,
        protocol_factory=factory.protocolFactory)
    thrift_file = open(filename, "wb")
    thrift_file.write(thrift_bytes)
    thrift_file.close()


class _FileTypeClass(object):
    '''
    An instance of this class represents filetypes abstractly; its
    members correspond to individual filetypes.  It probably doesn't
    make sense to have more than one instance of this class.
    '''

    def __init__(self, *names):
        self.CHOICES = tuple(names)
        for (i, name) in enumerate(names):
            if name == 'CHOICES':
                raise ValueError('%s is an invalid filetype name' % name)
            setattr(self, self._normalize(name), i)

    @classmethod
    def _normalize(cls, name):
        return name.replace('-', '_').upper()

    def lookup(self, ft):
        '''
        Return filetype (integer value) for ft, where ft may be
        a filetype name or (for convenience) the filetype integer
        value itself.
        '''

        if isinstance(ft, int):
            return ft
        elif isinstance(ft, str) or isinstance(ft, unicode):
            return getattr(self, self._normalize(ft))
        else:
            raise ValueError('unknown filetype %s' % str(ft))

    def add_argument(self, argparse_parser, flag='--input-filetype',
                     help_name='input file'):
        '''
        Add filetype argument to parser, return function that can be
        called on argparse namespace to retrieve argument value, e.g.,

        >>> get_filetype = add_argument(parser, ...)
        >>> ns = parser.parse_args()
        >>> filetype = get_filetype(ns)
        '''
        argparse_parser.add_argument(flag, type=str, choices=self.CHOICES,
                                     default=self.CHOICES[0],
                                     help='filetype for %s (choices: %s)' %
                                          (help_name, ', '.join(self.CHOICES)))

        def _get_value(ns):
            return getattr(ns, flag.lstrip('-').replace('-', '_'))
        return _get_value


FileType = _FileTypeClass(
    'auto',
    'zip',
    'tar', 'tar-gz', 'tar-bz2',
    'stream', 'stream-gz', 'stream-bz2',
)


class CommunicationReader(object):
    """Iterator/generator class for reading one or more Communications from a
    file

    The iterator returns a `(Communication, filename)` tuple

    Supported filetypes are:

    - a file with a single Communication
    - a file with multiple Communications concatenated together
    - a gzipped file with a single Communication
    - a gzipped file with multiple Communications concatenated together
    - a .tar.gz file with one or more Communications
    - a .zip file with one or more Communications

    -----

    Sample usage:

        for (comm, filename) in CommunicationReader('multiple_comms.tar.gz'):
            do_something(comm)
    """

    def __init__(self, filename, add_references=True, filetype=FileType.AUTO):
        filetype = FileType.lookup(filetype)

        self._add_references = add_references
        self._source_filename = filename

        if filetype == FileType.TAR:
            self.filetype = 'tar'
            self.tar = tarfile.open(filename, 'r|')

        elif filetype == FileType.TAR_GZ:
            self.filetype = 'tar'
            self.tar = tarfile.open(filename, 'r|gz')

        elif filetype == FileType.TAR_BZ2:
            self.filetype = 'tar'
            self.tar = tarfile.open(filename, 'r|bz2')

        elif filetype == FileType.ZIP:
            self.filetype = 'zip'
            self.zip = zipfile.ZipFile(filename, 'r')
            self.zip_infolist = self.zip.infolist()
            self.zip_infolist_index = 0

        elif filetype == FileType.STREAM:
            self.filetype = 'stream'
            f = open(filename, 'rb')

        elif filetype == FileType.STREAM_GZ:
            self.filetype = 'stream'
            f = gzip.open(filename, 'rb')

        elif filetype == FileType.STREAM_BZ2:
            self.filetype = 'stream'
            f = bz2.BZ2File(filename, 'r')

        elif filetype == FileType.AUTO:
            if tarfile.is_tarfile(filename):
                self.filetype = 'tar'
                self.tar = tarfile.open(filename, 'r|*')

            elif zipfile.is_zipfile(filename):
                self.filetype = 'zip'
                self.zip = zipfile.ZipFile(filename, 'r')
                self.zip_infolist = self.zip.infolist()
                self.zip_infolist_index = 0

            elif mimetypes.guess_type(filename)[1] == 'gzip':
                # this is not a true stream---is_tarfile will have
                # successfully seeked backwards on the file if we have
                # reached this point
                self.filetype = 'stream'
                f = gzip.open(filename, 'rb')

            elif mimetypes.guess_type(filename)[1] == 'bzip2':
                # this is not a true stream
                self.filetype = 'stream'
                f = bz2.BZ2File(filename, 'r')

            else:
                # this is not a true stream
                self.filetype = 'stream'
                f = open(filename, 'rb')

        else:
            raise ValueError('unknown filetype %d' % filetype)

        if self.filetype is 'stream':
            self.transport = TTransport.TFileObjectTransport(f)
            self.protocol = factory.createProtocol(self.transport)
            self.transport.open()

    def __iter__(self):
        return self

    def next(self):
        """Returns a `(Communication, filename)` tuple

        If the CommunicationReader is reading from an archive, then
        `filename` will be set to the name of the Communication file in
        the archive (e.g. `foo.concrete`), and not the name of the archive
        file (e.g. `bar.zip`).  If the CommunicationReader is reading from
        a concatenated file (instead of an archive), then all
        Communications extracted from the concatenated file will have the
        same value for the `filename` field.
        """
        if self.filetype is 'stream':
            return self._next_from_stream()
        elif self.filetype is 'tar':
            return self._next_from_tar()
        elif self.filetype is 'zip':
            return self._next_from_zip()

    def _next_from_stream(self):
        try:
            comm = Communication()
            comm.read(self.protocol)
            if self._add_references:
                add_references_to_communication(comm)
            return (comm, self._source_filename)
        except EOFError:
            self.transport.close()
            raise StopIteration

    def _next_from_tar(self):
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
                protocol_factory=factory.protocolFactory)
            if self._add_references:
                add_references_to_communication(comm)
            # hack to keep memory usage O(1)
            # (...but the real hack is tarfile :)
            self.tar.members = []
            return (comm, tarinfo.name)

    def _next_from_zip(self):
        if self.zip_infolist_index >= len(self.zip_infolist):
            raise StopIteration
        zipinfo = self.zip_infolist[self.zip_infolist_index]
        self.zip_infolist_index += 1
        comm = TSerialization.deserialize(
            Communication(),
            self.zip.open(zipinfo).read(),
            protocol_factory=factory.protocolFactory)
        if self._add_references:
            add_references_to_communication(comm)
        return (comm, zipinfo.filename)


class CommunicationWriter(object):
    """Class for writing one or more Communications to a file

    -----

    Sample usage:

        writer = CommunicationWriter('foo.concrete')
        writer.write(existing_comm_object)
        writer.close()
    """

    def __init__(self, filename=None):
        if filename is not None:
            self.open(filename)

    def close(self):
        self.file.close()

    def open(self, filename):
        self.file = open(filename, 'wb')

    def write(self, comm):
        thrift_bytes = TSerialization.serialize(
            comm, protocol_factory=factory.protocolFactory)
        self.file.write(thrift_bytes)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


class CommunicationWriterTar(object):
    """Class for writing one or more Communications to a .TAR archive

    -----

    Sample usage:

        writer = CommunicationWriterTar('multiple_comms.tar')
        writer.write(comm_object_one, 'comm_one.concrete')
        writer.write(comm_object_two, 'comm_two.concrete')
        writer.write(comm_object_three, 'comm_three.concrete')
        writer.close()
    """

    def __init__(self, tar_filename=None, gzip=False):
        self.gzip = gzip
        if tar_filename is not None:
            self.open(tar_filename)

    def close(self):
        self.tarfile.close()

    def open(self, tar_filename):
        self.tarfile = tarfile.open(tar_filename, 'w:gz' if self.gzip else 'w')

    def write(self, comm, comm_filename=None):
        if comm_filename is None:
            comm_filename = comm.uuid.uuidString + '.concrete'

        thrift_bytes = TSerialization.serialize(
            comm, protocol_factory=factory.protocolFactory)

        file_like_obj = cStringIO.StringIO(thrift_bytes)

        comm_tarinfo = tarfile.TarInfo()
        comm_tarinfo.type = tarfile.REGTYPE
        comm_tarinfo.name = comm_filename
        comm_tarinfo.size = len(thrift_bytes)
        comm_tarinfo.mode = 0644
        comm_tarinfo.mtime = time.time()
        comm_tarinfo.uid = os.getuid()
        comm_tarinfo.uname = pwd.getpwuid(os.getuid()).pw_name
        comm_tarinfo.gid = os.getgid()
        comm_tarinfo.gname = grp.getgrgid(os.getgid()).gr_name

        self.tarfile.addfile(comm_tarinfo, file_like_obj)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


class CommunicationWriterTGZ(CommunicationWriterTar):
    """Class for writing one or more Communications to a .TAR.GZ archive

    -----

    Sample usage:

        writer = CommunicationWriterTGZ('multiple_comms.tgz')
        writer.write(comm_object_one, 'comm_one.concrete')
        writer.write(comm_object_two, 'comm_two.concrete')
        writer.write(comm_object_three, 'comm_three.concrete')
        writer.close()
    """

    def __init__(self, tar_filename=None):
        super(CommunicationWriterTGZ, self).__init__(tar_filename, gzip=True)
