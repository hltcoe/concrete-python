from pytest import fixture, mark
from concrete.util.file_io import CommunicationReader
from concrete.validate import validate_communication
from concrete.util.concrete_uuid import compress_uuids
import os
from subprocess import Popen, PIPE
from tempfile import mkstemp


@fixture
def output_file(request):
    (fd, path) = mkstemp()
    os.close(fd)

    def _remove():
        if os.path.exists(path):
            os.remove(path)

    request.addfinalizer(_remove)
    return path


@mark.parametrize('args', [
    (),
    ('--verify',),
    ('--verify', '--single-analytic'),
    ('--single-analytic',),
])
def test_compress_uuids(output_file, args):
    input_file = 'tests/testdata/simple.tar.gz'

    p = Popen([
        'scripts/compress-uuids.py',
        input_file,
        output_file
    ] + list(args), stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()

    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, comm_filename) = it.next()
    assert comm_filename == 'simple_1.concrete'
    assert comm.id == 'one'
    assert validate_communication(comm)

    (comm, comm_filename) = it.next()
    assert comm_filename == 'simple_2.concrete'
    assert comm.id == 'two'
    assert validate_communication(comm)

    (comm, comm_filename) = it.next()
    assert comm_filename == 'simple_3.concrete'
    assert comm.id == 'three'
    assert validate_communication(comm)

    assert os.stat(output_file).st_size < os.stat(input_file).st_size

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


@mark.parametrize('reader_kwargs,compress_kwargs', [
    (dict(add_references=False), dict()),
    (dict(add_references=False), dict(verify=True)),
    (dict(add_references=False), dict(verify=False)),
    (dict(add_references=False), dict(verify=True, single_analytic=True)),
    (dict(add_references=False), dict(verify=False, single_analytic=True)),
    (dict(add_references=False), dict(verify=True, single_analytic=False)),
    (dict(add_references=False), dict(verify=False, single_analytic=False)),
    (dict(add_references=False), dict(single_analytic=False)),
    (dict(add_references=False), dict(single_analytic=True)),
    (dict(add_references=True), dict()),
    mark.xfail(
        (dict(add_references=True), dict(verify=True)),
        strict=True,
    ),
    (dict(add_references=True), dict(verify=False)),
    mark.xfail(
        (dict(add_references=True), dict(verify=True, single_analytic=True)),
        strict=True,
    ),
    (dict(add_references=True), dict(verify=False, single_analytic=True)),
    mark.xfail(
        (dict(add_references=True), dict(verify=True, single_analytic=False)),
        strict=True,
    ),
    (dict(add_references=True), dict(verify=False, single_analytic=False)),
    (dict(add_references=True), dict(single_analytic=False)),
    (dict(add_references=True), dict(single_analytic=True)),
])
def test_compress_uuids_api(reader_kwargs, compress_kwargs):
    input_file = 'tests/testdata/simple.tar.gz'
    reader = CommunicationReader(input_file, **reader_kwargs)
    it = iter(reader)

    (comm, _) = it.next()
    (new_comm, uc) = compress_uuids(comm, **compress_kwargs)
    assert new_comm.id == 'one'
    assert comm.id == new_comm.id
    assert validate_communication(new_comm)

    (comm, _) = it.next()
    (new_comm, uc) = compress_uuids(comm, **compress_kwargs)
    assert new_comm.id == 'two'
    assert comm.id == new_comm.id
    assert validate_communication(new_comm)

    (comm, _) = it.next()
    (new_comm, uc) = compress_uuids(comm, **compress_kwargs)
    assert new_comm.id == 'three'
    assert comm.id == new_comm.id
    assert validate_communication(new_comm)

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False
