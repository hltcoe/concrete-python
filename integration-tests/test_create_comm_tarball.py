# -*- coding: utf-8 -*-


from pytest import fixture
from concrete.util.file_io import CommunicationReader
from concrete.validate import validate_communication
import os
from subprocess import Popen, PIPE
from tempfile import mkstemp


@fixture
def text_l0():
    return u'''\
Madame Magloire comprit, et elle alla chercher sur la cheminée de la \
chambre à coucher de monseigneur les deux chandeliers d'argent \
qu'elle posa sur la table tout allumés.
'''


@fixture
def text_l1():
    return u'''\
—Monsieur le curé, dit l'homme, vous êtes bon. Vous ne me méprisez \
pas. Vous me recevez chez vous. Vous allumez vos cierges pour moi. \
Je ne vous ai pourtant pas caché d'où je viens et que je suis un homme \
malheureux.
'''


@fixture
def text_l1_s0():
    return u'''\
—Monsieur le curé, dit l'homme, vous êtes bon.
'''


@fixture
def text_l1_s1():
    return u'''\
Vous ne me méprisez pas.
'''


@fixture
def text_l1_s2():
    return u'''\
Vous me recevez chez vous.
'''


@fixture
def text_l1_s3():
    return u'''\
Vous allumez vos cierges pour moi.
'''


@fixture
def text_l1_s4():
    return u'''\
Je ne vous ai pourtant pas caché d'où je viens et que je suis un homme \
malheureux.
'''


@fixture
def output_file(request):
    (fd, path) = mkstemp()
    os.close(fd)

    def _remove():
        if os.path.exists(path):
            os.remove(path)

    request.addfinalizer(_remove)
    return path


def test_create_comm_tarball(output_file, text_l0, text_l1):
    p = Popen([
        'scripts/create-comm-tarball.py',
        'tests/testdata/les-deux-chandeliers.tar.gz',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = it.next()
    assert comm.id == 'les-deux-chandeliers/l0.txt'
    assert validate_communication(comm)
    assert comm.text == text_l0
    assert comm.sectionList is None

    (comm, _) = it.next()
    assert comm.id == 'les-deux-chandeliers/l1.txt'
    assert validate_communication(comm)
    assert comm.text == text_l1
    assert comm.sectionList is None

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


def test_create_comm_tarball_stdin(output_file, text_l0, text_l1):
    p = Popen([
        'scripts/create-comm-tarball.py',
        '-',
        output_file
    ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    with open('tests/testdata/les-deux-chandeliers.tar.gz', 'rb') as f:
        (stdout, stderr) = p.communicate(f.read())
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = it.next()
    assert comm.id == 'les-deux-chandeliers/l0.txt'
    assert validate_communication(comm)
    assert comm.text == text_l0
    assert comm.sectionList is None

    (comm, _) = it.next()
    assert comm.id == 'les-deux-chandeliers/l1.txt'
    assert validate_communication(comm)
    assert comm.text == text_l1
    assert comm.sectionList is None

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


def test_create_comm_tarball_stdout(output_file, text_l0, text_l1):
    p = Popen([
        'scripts/create-comm-tarball.py',
        'tests/testdata/les-deux-chandeliers.tar.gz',
        '-'
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    with open(output_file, 'wb') as f:
        f.write(stdout)

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = it.next()
    assert comm.id == 'les-deux-chandeliers/l0.txt'
    assert validate_communication(comm)
    assert comm.text == text_l0
    assert comm.sectionList is None

    (comm, _) = it.next()
    assert comm.id == 'les-deux-chandeliers/l1.txt'
    assert validate_communication(comm)
    assert comm.text == text_l1
    assert comm.sectionList is None

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


def test_create_comm_tarball_log_every(output_file, text_l0, text_l1):
    p = Popen([
        'scripts/create-comm-tarball.py',
        '--log-level', 'INFO',
        '--log-interval', '1',
        'tests/testdata/les-deux-chandeliers.tar.gz',
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
    assert comm.id == 'les-deux-chandeliers/l0.txt'
    assert validate_communication(comm)
    assert comm.text == text_l0
    assert comm.sectionList is None

    (comm, _) = it.next()
    assert comm.id == 'les-deux-chandeliers/l1.txt'
    assert validate_communication(comm)
    assert comm.text == text_l1
    assert comm.sectionList is None

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


def test_create_comm_tarball_annotated(output_file, text_l0, text_l1):
    p = Popen([
        'scripts/create-comm-tarball.py',
        '--annotation-level', 'section',
        'tests/testdata/les-deux-chandeliers.tar.gz',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = it.next()
    assert comm.id == 'les-deux-chandeliers/l0.txt'
    assert validate_communication(comm)
    assert comm.text == text_l0
    assert len(comm.sectionList) == 1

    (comm, _) = it.next()
    assert comm.id == 'les-deux-chandeliers/l1.txt'
    assert validate_communication(comm)
    assert comm.text == text_l1
    assert len(comm.sectionList) == 1

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


def test_create_comm_tarball_per_line(output_file, text_l0,
                                      text_l1_s0, text_l1_s1, text_l1_s2,
                                      text_l1_s3, text_l1_s4):
    p = Popen([
        'scripts/create-comm-tarball.py',
        '--per-line',
        'tests/testdata/les-deux-chandeliers-perline.tar.gz',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = it.next()
    assert comm.id == 'les-deux-chandeliers-perline/l0.txt/0'
    assert validate_communication(comm)
    assert comm.text == text_l0
    assert comm.sectionList is None

    (comm, _) = it.next()
    assert comm.id == 'les-deux-chandeliers-perline/l1.txt/0'
    assert validate_communication(comm)
    assert comm.text == text_l1_s0
    assert comm.sectionList is None

    (comm, _) = it.next()
    assert comm.id == 'les-deux-chandeliers-perline/l1.txt/1'
    assert validate_communication(comm)
    assert comm.text == text_l1_s1
    assert comm.sectionList is None

    (comm, _) = it.next()
    assert comm.id == 'les-deux-chandeliers-perline/l1.txt/2'
    assert validate_communication(comm)
    assert comm.text == text_l1_s2
    assert comm.sectionList is None

    (comm, _) = it.next()
    assert comm.id == 'les-deux-chandeliers-perline/l1.txt/3'
    assert validate_communication(comm)
    assert comm.text == text_l1_s3
    assert comm.sectionList is None

    (comm, _) = it.next()
    assert comm.id == 'les-deux-chandeliers-perline/l1.txt/4'
    assert validate_communication(comm)
    assert comm.text == text_l1_s4
    assert comm.sectionList is None

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False
