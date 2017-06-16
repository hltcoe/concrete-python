"""Code for reading and writing Concrete Communications
"""
from __future__ import unicode_literals

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

from gzip import open as gzip_open
import bz2
import mimetypes
import tarfile
import zipfile

import os
import time

from thrift import TSerialization
from thrift.transport import TTransport

from ..communication.ttypes import Communication
from ..structure.ttypes import TokenLattice
from .references import add_references_to_communication
from .thrift_factory import factory


if os.name == 'nt':
    def _get_uid():
        return 0

    def _get_gid():
        return 0

    def _get_username():
        return ''

    def _get_groupname():
        return ''

else:
    import pwd
    import grp

    def _get_uid():
        return os.getuid()

    def _get_gid():
        return os.getgid()

    def _get_username():
        return pwd.getpwuid(_get_uid()).pw_name

    def _get_groupname():
        return grp.getgrgid(_get_gid()).gr_name


def read_thrift_from_file(thrift_obj, filename):
    """Instantiate Thrift object from contents of named file

    The Thrift file is assumed to be encoded using TCompactProtocol

    **WARNING** - Thrift deserialization tends to fail silently.  For
    example, the Thrift libraries will not complain if you try to
    deserialize data from the file `/dev/urandom`.

    Args:
        thrift_obj: A Thrift object (e.g. a Communication object)
        filename (str):  A filename string

    Returns:
        The Thrift object that was passed in as an argument
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
        communication_filename (str): String with filename
        add_references (bool): If True, calls
           :func:`concrete.util.references.add_references_to_communication`
           on :class:`.Communication` read from file

    Returns:
        Communication:
    """
    comm = read_thrift_from_file(Communication(), communication_filename)
    if add_references:
        add_references_to_communication(comm)
    return comm


def read_tokenlattice_from_file(tokenlattice_filename):
    """Read a :class:`.TokenLattice` from a file

    Args:
        tokenlattice_filename (str): Name of file containing serialized
            :class:`.TokenLattice`

    Returns:
        TokenLattice:
    """
    return read_thrift_from_file(TokenLattice(), tokenlattice_filename)


def write_communication_to_file(communication, communication_filename):
    """Write a :class:`.Communication` to a file

    Args:
        communication (Communication): communication to write
        communication_filename (str): path of file to write to
    """
    return write_thrift_to_file(communication, communication_filename)


def write_thrift_to_file(thrift_obj, filename):
    """Write a Thrift object to a file

    Args:
        thrift_obj: Thrift object to write
        filename (str): path of file to write to
    """
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
        Convenience method:
        Look up and return integer filetype corresponding to filetype
        name (or, if given the integer filetype, return that integer).

        Args:
            ft: filetype name (str) or integer value

        Returns:
            filetype (integer value) for ft
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


class ThriftReader(object):
    """Iterator/generator class for reading one or more Thrift structures
    from a file

    The iterator returns a `(obj, filename)` tuple where obj is an object
    of type thrift_type.

    Supported filetypes are:

    - a file with a single Thrift structure
    - a file with multiple Thrift structures concatenated together
    - a gzipped file with a single Thrift structure
    - a gzipped file with multiple Thrift structures concatenated
      together
    - a .tar.gz file with one or more Thrift structures
    - a .zip file with one or more Thrift structures

    Sample usage::

        for (comm, filename) in ThriftReader(Communication,
                                             'multiple_comms.tar.gz'):
            do_something(comm)
    """

    def __init__(self, thrift_type, filename,
                 postprocess=None, filetype=FileType.AUTO):
        """
        Args:
            thrift_type: Class for Thrift type, e.g. Communication, TokenLattice
            filename (str):
            postprocess (function): A post-processing function that is called
                with the Thrift object as argument each time a Thrift object
                is read from the file
            filetype (FileType): Expected type of file.  Default value is
                `FileType.AUTO`, where function will try to automatically
                determine file type.
        """
        filetype = FileType.lookup(filetype)

        self._thrift_type = thrift_type
        if postprocess is None:
            def _noop(obj):
                return
            self._postprocess = _noop
        else:
            self._postprocess = postprocess
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
            f = gzip_open(filename, 'rb')

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
                f = gzip_open(filename, 'rb')

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

        if self.filetype == 'stream':
            self.transport = TTransport.TFileObjectTransport(f)
            self.protocol = factory.createProtocol(self.transport)
            self.transport.open()

    def __iter__(self):
        return self

    def __next__(self):
        """Returns a `(obj, filename)` tuple where obj is an object
        of type thrift_type.

        If the ThriftReader is reading from an archive, then
        `filename` will be set to the name of the Thrift entry in
        the archive (e.g. `foo.concrete`), and not the name of the
        archive file (e.g. `bar.zip`).  If the ThriftReader is reading
        from a concatenated file (instead of an archive), then all
        Thrift structures extracted from the concatenated file will have
        the same value for the `filename` field.
        """
        if self.filetype == 'stream':
            return self._next_from_stream()
        elif self.filetype == 'tar':
            return self._next_from_tar()
        elif self.filetype == 'zip':
            return self._next_from_zip()
        else:
            raise ValueError('unknown filetype %s' % self.filetype)

    def next(self):
        return self.__next__()

    def _next_from_stream(self):
        try:
            comm = self._thrift_type()
            comm.read(self.protocol)
            self._postprocess(comm)
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
            if filename[0] == '.' and filename[1] == '_':
                # Ignore attribute files created by OS X tar
                continue
            comm = TSerialization.deserialize(
                self._thrift_type(),
                self.tar.extractfile(tarinfo).read(),
                protocol_factory=factory.protocolFactory)
            self._postprocess(comm)
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
            self._thrift_type(),
            self.zip.open(zipinfo).read(),
            protocol_factory=factory.protocolFactory)
        self._postprocess(comm)
        return (comm, zipinfo.filename)


class CommunicationReader(ThriftReader):
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

    Sample usage::

        for (comm, filename) in CommunicationReader('multiple_comms.tar.gz'):
            do_something(comm)
    """

    def __init__(self, filename, add_references=True, filetype=FileType.AUTO):
        """
        Args:
            filename (str): path of file to read from
            add_references (bool): If True, calls
               :func:`concrete.util.references.add_references_to_communication`
               on all :class:`.Communication` objects read from file
            filetype (FileType): Expected type of file.  Default value is
                `FileType.AUTO`, where function will try to automatically
                determine file type.
        """
        super(CommunicationReader, self).__init__(
            Communication,
            filename,
            postprocess=(add_references_to_communication
                         if add_references
                         else None),
            filetype=filetype)


class CommunicationWriter(object):
    """Class for writing one or more Communications to a file

    Sample usage::

        writer = CommunicationWriter('foo.concrete')
        writer.write(existing_comm_object)
        writer.close()
    """

    def __init__(self, filename=None, gzip=False):
        """
        Args:
            filename (str): if specified, open file at this path
                during construction (a file can alternatively be opened
                after construction using the open method)
            gzip (bool): Flag indicating if file should be
                compressed with gzip
        """
        self.gzip = gzip
        if filename is not None:
            self.open(filename)

    def close(self):
        '''
        Close file.
        '''
        self.file.close()

    def open(self, filename):
        """
        Open specified file for writing.  File will be compressed
        if the gzip flag of the constructor was set to True.

        Args:
            filename (str): path to file to open for writing
        """
        if self.gzip:
            self.file = gzip_open(filename, 'wb')
        else:
            self.file = open(filename, 'wb')

    def write(self, comm):
        """
        Args:
            comm (Communication): communication to write to file
        """
        thrift_bytes = TSerialization.serialize(
            comm, protocol_factory=factory.protocolFactory)
        self.file.write(thrift_bytes)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


class CommunicationWriterTar(object):
    """Class for writing one or more Communications to a .TAR archive

    Sample usage::

        writer = CommunicationWriterTar('multiple_comms.tar')
        writer.write(comm_object_one, 'comm_one.concrete')
        writer.write(comm_object_two, 'comm_two.concrete')
        writer.write(comm_object_three, 'comm_three.concrete')
        writer.close()
    """

    def __init__(self, tar_filename=None, gzip=False):
        """
        Args:
            tar_filename (str): if specified, open file at this path
                during construction (a file can alternatively be opened
                after construction using the open method)
            gzip (bool): Flag indicating if .TAR file should be
                compressed with gzip
        """
        self.gzip = gzip
        if tar_filename is not None:
            self.open(tar_filename)

    def close(self):
        '''
        Close tar file.
        '''
        self.tarfile.close()

    def open(self, tar_filename):
        """
        Open specified tar file for writing.  File will be compressed
        if the gzip flag of the constructor was set to True.

        Args:
            tar_filename (str): path to file to open for writing
        """
        self.tarfile = tarfile.open(tar_filename, 'w:gz' if self.gzip else 'w')

    def write(self, comm, comm_filename=None):
        """
        Args:
            comm (Communication): communication to write to tar file
            comm_filename (str): desired filename of communication
                within tar file (by default the filename will be the
                communication id appended with a .concrete extension)
        """
        if comm_filename is None:
            comm_filename = comm.id + '.concrete'

        thrift_bytes = TSerialization.serialize(
            comm, protocol_factory=factory.protocolFactory)

        file_like_obj = BytesIO(thrift_bytes)

        comm_tarinfo = tarfile.TarInfo()
        comm_tarinfo.type = tarfile.REGTYPE
        comm_tarinfo.name = comm_filename
        comm_tarinfo.size = len(thrift_bytes)
        comm_tarinfo.mode = 0o644
        comm_tarinfo.mtime = time.time()
        comm_tarinfo.uid = _get_uid()
        comm_tarinfo.uname = _get_username()
        comm_tarinfo.gid = _get_gid()
        comm_tarinfo.gname = _get_groupname()

        self.tarfile.addfile(comm_tarinfo, file_like_obj)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


class CommunicationWriterTGZ(CommunicationWriterTar):
    """Class for writing one or more Communications to a .TAR.GZ archive

    Sample usage::

        writer = CommunicationWriterTGZ('multiple_comms.tgz')
        writer.write(comm_object_one, 'comm_one.concrete')
        writer.write(comm_object_two, 'comm_two.concrete')
        writer.write(comm_object_three, 'comm_three.concrete')
        writer.close()
    """

    def __init__(self, tar_filename=None):
        super(CommunicationWriterTGZ, self).__init__(tar_filename, gzip=True)
