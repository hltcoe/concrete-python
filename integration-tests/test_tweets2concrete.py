# -*- coding: utf-8 -*-


from __future__ import unicode_literals
from pytest import fixture, mark
from concrete.util import CommunicationReader
from concrete.validate import validate_communication
import sys
import json
from subprocess import Popen, PIPE


def assert_first_comm(comm):
    assert comm.id == '238426131689242624'
    assert comm.startTime == 1345680194
    assert comm.endTime == 1345680194
    assert validate_communication(comm)


def assert_second_comm(comm):
    assert comm.id == '238426131689242625'
    assert comm.startTime == 1345680195
    assert comm.endTime == 1345680195
    assert validate_communication(comm)


@fixture
def log_conf(tmpdir):
    log_path = str(tmpdir / 'log')
    conf_path = str(tmpdir / 'log.conf')

    with open(conf_path, 'w') as f:
        json.dump(
            dict(
                version=1,
                root=dict(
                    level='INFO',
                    handlers=['file'],
                ),
                formatters=dict(
                    medium=dict(
                        format='%(asctime)-15s %(levelname)s: %(message)s',
                    ),
                ),
                handlers=dict(
                    file={
                        'class': 'logging.FileHandler',
                        'formatter': 'medium',
                        'filename': log_path,
                    },
                ),
            ),
            f
        )

    yield (conf_path, log_path)


@fixture
def output_file(tmpdir):
    yield str(tmpdir / 'output.comm')


def test_tweets2concrete(output_file):
    p = Popen([
        sys.executable,
        'scripts/tweets2concrete.py',
        'tests/testdata/tweets.json',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = next(it)
    assert_first_comm(comm)

    (comm, _) = next(it)
    assert_second_comm(comm)

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False


@mark.posix
def test_tweets2concrete_stdin(output_file):
    p = Popen([
        sys.executable,
        'scripts/tweets2concrete.py',
        '-',
        output_file
    ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    with open('tests/testdata/tweets.json', 'rb') as f:
        (stdout, stderr) = p.communicate(f.read())
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = next(it)
    assert_first_comm(comm)

    (comm, _) = next(it)
    assert_second_comm(comm)

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False


@mark.posix
def test_tweets2concrete_stdout(output_file):
    p = Popen([
        sys.executable,
        'scripts/tweets2concrete.py',
        'tests/testdata/tweets.json',
        '-'
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    with open(output_file, 'wb') as f:
        f.write(stdout)

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = next(it)
    assert_first_comm(comm)

    (comm, _) = next(it)
    assert_second_comm(comm)

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_multiproc(output_file):
    p = Popen([
        sys.executable,
        'scripts/tweets2concrete.py',
        '--num-proc', '2',
        'tests/testdata/tweets.json',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = next(it)
    assert_first_comm(comm)

    (comm, _) = next(it)
    assert_second_comm(comm)

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_log_every(output_file):
    p = Popen([
        sys.executable,
        'scripts/tweets2concrete.py',
        '--log-level', 'INFO',
        '--log-interval', '1',
        'tests/testdata/tweets.json',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0
    assert len([line
                for line in stderr.decode('utf-8').strip().split('\n')
                if 'INFO' in line]) >= 2

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = next(it)
    assert_first_comm(comm)

    (comm, _) = next(it)
    assert_second_comm(comm)

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_unicode(output_file):
    p = Popen([
        sys.executable,
        'scripts/tweets2concrete.py',
        'tests/testdata/tweets.unicode.json',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = next(it)
    assert_first_comm(comm)
    assert validate_communication(comm)

    (comm, _) = next(it)
    assert_second_comm(comm)

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_gz(output_file):
    p = Popen([
        sys.executable,
        'scripts/tweets2concrete.py',
        'tests/testdata/tweets.json.gz',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = next(it)
    assert_first_comm(comm)

    (comm, _) = next(it)
    assert_second_comm(comm)

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_incomplete_gz(output_file):
    p = Popen([
        sys.executable,
        'scripts/tweets2concrete.py',
        '--catch-ioerror',
        'tests/testdata/tweets.json.incomplete.gz',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = next(it)
    assert_first_comm(comm)

    (comm, _) = next(it)
    assert_second_comm(comm)

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_incomplete_gz_multiproc(output_file):
    p = Popen([
        sys.executable,
        'scripts/tweets2concrete.py',
        '--num-proc', '2',
        '--catch-ioerror',
        'tests/testdata/tweets.json.incomplete.gz',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = next(it)
    assert_first_comm(comm)

    (comm, _) = next(it)
    assert_second_comm(comm)

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_log_config(log_conf, output_file):
    (log_conf_path, log_path) = log_conf
    p = Popen([
        sys.executable,
        'scripts/tweets2concrete.py',
        '--log-conf-path', log_conf_path,
        '--log-interval', '1',
        'tests/testdata/tweets.json',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert stdout.decode('utf-8') == ''
    assert stderr.decode('utf-8') == ''
    assert p.returncode == 0

    with open(log_path) as f:
        data = f.read()
        assert len([line
                    for line in data.strip().split('\n')
                    if 'INFO' in line]) >= 2

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = next(it)
    assert_first_comm(comm)

    (comm, _) = next(it)
    assert_second_comm(comm)

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_deleted(output_file):
    p = Popen([
        sys.executable,
        'scripts/tweets2concrete.py',
        'tests/testdata/tweets.deleted.json',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = next(it)
    assert_first_comm(comm)

    (comm, _) = next(it)
    assert_second_comm(comm)

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_bad_line(output_file):
    p = Popen([
        sys.executable,
        'scripts/tweets2concrete.py',
        '--skip-bad-lines',
        'tests/testdata/tweets.bad-line.json',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = next(it)
    assert_first_comm(comm)

    (comm, _) = next(it)
    assert_second_comm(comm)

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_bad_line_unicode(output_file):
    p = Popen([
        sys.executable,
        'scripts/tweets2concrete.py',
        '--skip-bad-lines',
        'tests/testdata/tweets.bad-line-unicode.json',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = next(it)
    assert_first_comm(comm)

    (comm, _) = next(it)
    assert_second_comm(comm)

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_invalid(output_file):
    p = Popen([
        sys.executable,
        'scripts/tweets2concrete.py',
        '--skip-invalid-comms',
        'tests/testdata/tweets.invalid.json',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = next(it)
    assert_first_comm(comm)

    (comm, _) = next(it)
    assert_second_comm(comm)

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False
