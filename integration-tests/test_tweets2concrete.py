# -*- coding: utf-8 -*-


from pytest import fixture
from concrete.util.file_io import CommunicationReader
from concrete.validate import validate_communication
import os
from subprocess import Popen, PIPE
from tempfile import mkstemp


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
def log_conf(request):
    (fd, log_path) = mkstemp()
    os.close(fd)

    (fd, conf_path) = mkstemp()
    os.close(fd)
    with open(conf_path, 'w') as f:
        f.write('''{
  "version": 1,
  "root": {
    "level": "INFO",
    "handlers": ["file"]
  },
  "formatters": {
    "medium": {
      "format": "%%(asctime)-15s %%(levelname)s: %%(message)s"
    }
  },
  "handlers": {
    "file": {
      "class": "logging.FileHandler",
      "formatter": "medium",
      "filename": "%s"
    }
  }
}
''' % log_path)

    def _remove():
        if os.path.exists(conf_path):
            os.remove(conf_path)
        if os.path.exists(log_path):
            os.remove(log_path)

    request.addfinalizer(_remove)
    return (conf_path, log_path)


@fixture
def output_file(request):
    (fd, path) = mkstemp()
    os.close(fd)

    def _remove():
        if os.path.exists(path):
            os.remove(path)

    request.addfinalizer(_remove)
    return path


def test_tweets2concrete(output_file):
    p = Popen([
        'scripts/tweets2concrete.py',
        'tests/testdata/tweets.json',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = it.next()
    assert_first_comm(comm)

    (comm, _) = it.next()
    assert_second_comm(comm)

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_stdin(output_file):
    p = Popen([
        'scripts/tweets2concrete.py',
        '-',
        output_file
    ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    with open('tests/testdata/tweets.json', 'rb') as f:
        (stdout, stderr) = p.communicate(f.read())
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = it.next()
    assert_first_comm(comm)

    (comm, _) = it.next()
    assert_second_comm(comm)

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_stdout(output_file):
    p = Popen([
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

    (comm, _) = it.next()
    assert_first_comm(comm)

    (comm, _) = it.next()
    assert_second_comm(comm)

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_multiproc(output_file):
    p = Popen([
        'scripts/tweets2concrete.py',
        '--num-proc', '2',
        'tests/testdata/tweets.json',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = it.next()
    assert_first_comm(comm)

    (comm, _) = it.next()
    assert_second_comm(comm)

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_log_every(output_file):
    p = Popen([
        'scripts/tweets2concrete.py',
        '--log-level', 'INFO',
        '--log-interval', '1',
        'tests/testdata/tweets.json',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0
    assert len([line
                for line in stderr.strip().split('\n')
                if 'INFO' in line]) >= 2

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = it.next()
    assert_first_comm(comm)

    (comm, _) = it.next()
    assert_second_comm(comm)

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_unicode(output_file):
    p = Popen([
        'scripts/tweets2concrete.py',
        'tests/testdata/tweets.unicode.json',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = it.next()
    assert_first_comm(comm)
    assert validate_communication(comm)

    (comm, _) = it.next()
    assert_second_comm(comm)

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_gz(output_file):
    p = Popen([
        'scripts/tweets2concrete.py',
        'tests/testdata/tweets.json.gz',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = it.next()
    assert_first_comm(comm)

    (comm, _) = it.next()
    assert_second_comm(comm)

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_incomplete_gz(output_file):
    p = Popen([
        'scripts/tweets2concrete.py',
        '--catch-ioerror',
        'tests/testdata/tweets.json.incomplete.gz',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = it.next()
    assert_first_comm(comm)

    (comm, _) = it.next()
    assert_second_comm(comm)

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_incomplete_gz_multiproc(output_file):
    p = Popen([
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

    (comm, _) = it.next()
    assert_first_comm(comm)

    (comm, _) = it.next()
    assert_second_comm(comm)

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_log_config(log_conf, output_file):
    (log_conf_path, log_path) = log_conf
    p = Popen([
        'scripts/tweets2concrete.py',
        '--log-conf-path', log_conf_path,
        '--log-interval', '1',
        'tests/testdata/tweets.json',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0
    assert len(stdout) == 0
    assert len(stderr) == 0

    with open(log_path) as f:
        data = f.read()
        assert len([line
                    for line in data.strip().split('\n')
                    if 'INFO' in line]) >= 2

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = it.next()
    assert_first_comm(comm)

    (comm, _) = it.next()
    assert_second_comm(comm)

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_deleted(output_file):
    p = Popen([
        'scripts/tweets2concrete.py',
        'tests/testdata/tweets.deleted.json',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = it.next()
    assert_first_comm(comm)

    (comm, _) = it.next()
    assert_second_comm(comm)

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_bad_line(output_file):
    p = Popen([
        'scripts/tweets2concrete.py',
        '--skip-bad-lines',
        'tests/testdata/tweets.bad-line.json',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = it.next()
    assert_first_comm(comm)

    (comm, _) = it.next()
    assert_second_comm(comm)

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_bad_line_unicode(output_file):
    p = Popen([
        'scripts/tweets2concrete.py',
        '--skip-bad-lines',
        'tests/testdata/tweets.bad-line-unicode.json',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = it.next()
    assert_first_comm(comm)

    (comm, _) = it.next()
    assert_second_comm(comm)

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


def test_tweets2concrete_invalid(output_file):
    p = Popen([
        'scripts/tweets2concrete.py',
        '--skip-invalid-comms',
        'tests/testdata/tweets.invalid.json',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = it.next()
    assert_first_comm(comm)

    (comm, _) = it.next()
    assert_second_comm(comm)

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False
