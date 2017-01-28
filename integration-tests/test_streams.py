from __future__ import unicode_literals
from pytest import fixture
from concrete.util import (
    CommunicationReader, FileType
)
import os
import tempfile

from multiprocessing import Process

from pytest import mark


@fixture
def fifo(request):
    (fd, path) = tempfile.mkstemp()
    os.close(fd)
    os.remove(path)
    os.mkfifo(path)  # not quite secure...

    def _remove():
        if os.path.exists(path):
            os.remove(path)
    request.addfinalizer(_remove)

    return path


def write_fifo(input_path, fifo_path):
    with open(input_path, 'rb') as in_f:
        with open(fifo_path, 'wb') as out_f:
            out_f.write(in_f.read())


@mark.posix
def test_concatenated(fifo):
    input_path = 'tests/testdata/simple_concatenated'
    p = Process(target=write_fifo, args=(input_path, fifo))
    p.start()

    reader = CommunicationReader(fifo, filetype=FileType.STREAM)
    it = iter(reader)

    (comm, path) = next(it)
    assert comm.id == 'one'

    (comm, path) = next(it)
    assert comm.id == 'two'

    (comm, path) = next(it)
    assert comm.id == 'three'

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False

    p.join()


@mark.posix
def test_concatenated_bz2(fifo):
    '''
    Note: concatenated_gz does not work, complaining about a tell (seek).
    tar_gz does work because the r|gz mode in tarfile results in direct
    calls to zlib for decompression.  gzip (which wraps zlib and is used
    in CommunicationReader for non-tar gz files) is the culprit.
    '''

    input_path = 'tests/testdata/simple_concatenated.bz2'
    p = Process(target=write_fifo, args=(input_path, fifo))
    p.start()

    reader = CommunicationReader(fifo, filetype=FileType.STREAM_BZ2)
    it = iter(reader)

    (comm, path) = next(it)
    assert comm.id == 'one'

    (comm, path) = next(it)
    assert comm.id == 'two'

    (comm, path) = next(it)
    assert comm.id == 'three'

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False

    p.join()


@mark.posix
def test_tar(fifo):
    input_path = 'tests/testdata/simple.tar'
    p = Process(target=write_fifo, args=(input_path, fifo))
    p.start()

    reader = CommunicationReader(fifo, filetype=FileType.TAR)
    it = iter(reader)

    (comm, path) = next(it)
    assert comm.id == 'one'

    (comm, path) = next(it)
    assert comm.id == 'two'

    (comm, path) = next(it)
    assert comm.id == 'three'

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False

    p.join()


@mark.posix
def test_tar_gz(fifo):
    input_path = 'tests/testdata/simple.tar.gz'
    p = Process(target=write_fifo, args=(input_path, fifo))
    p.start()

    reader = CommunicationReader(fifo, filetype=FileType.TAR_GZ)
    it = iter(reader)

    (comm, path) = next(it)
    assert comm.id == 'one'

    (comm, path) = next(it)
    assert comm.id == 'two'

    (comm, path) = next(it)
    assert comm.id == 'three'

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False

    p.join()


@mark.posix
def test_tar_bz2(fifo):
    input_path = 'tests/testdata/simple.tar.bz2'
    p = Process(target=write_fifo, args=(input_path, fifo))
    p.start()

    reader = CommunicationReader(fifo, filetype=FileType.TAR_BZ2)
    it = iter(reader)

    (comm, path) = next(it)
    assert comm.id == 'one'

    (comm, path) = next(it)
    assert comm.id == 'two'

    (comm, path) = next(it)
    assert comm.id == 'three'

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False

    p.join()
