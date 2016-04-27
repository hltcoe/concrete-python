# -*- coding: utf-8 -*-


from pytest import fixture
from concrete.util.file_io import CommunicationReader
from concrete.validate import validate_communication
import os
from subprocess import Popen, PIPE
from tempfile import mkstemp


@fixture
def text():
    return u'''\
Madame Magloire comprit, et elle alla chercher sur la cheminée de la \
chambre à coucher de monseigneur les deux chandeliers d'argent \
qu'elle posa sur la table tout allumés.

—Monsieur le curé, dit l'homme, vous êtes bon. Vous ne me méprisez \
pas. Vous me recevez chez vous. Vous allumez vos cierges pour moi. \
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


def test_create_comm(output_file, text):
    p = Popen([
        'scripts/create-comm.py',
        'tests/testdata/les-deux-chandeliers.txt',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = it.next()
    assert comm.id == 'tests/testdata/les-deux-chandeliers.txt'
    assert validate_communication(comm)
    assert comm.text == text
    assert comm.sectionList is None

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


def test_create_comm_stdin(output_file, text):
    p = Popen([
        'scripts/create-comm.py',
        '-',
        output_file
    ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    with open('tests/testdata/les-deux-chandeliers.txt', 'rb') as f:
        (stdout, stderr) = p.communicate(f.read())
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = it.next()
    assert comm.id == '/dev/fd/0'
    assert validate_communication(comm)
    assert comm.text == text
    assert comm.sectionList is None

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


def test_create_comm_stdout(output_file, text):
    p = Popen([
        'scripts/create-comm.py',
        'tests/testdata/les-deux-chandeliers.txt',
        '-'
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    with open(output_file, 'wb') as f:
        f.write(stdout)

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = it.next()
    assert comm.id == 'tests/testdata/les-deux-chandeliers.txt'
    assert validate_communication(comm)
    assert comm.text == text
    assert comm.sectionList is None

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False


def test_create_comm_annotated(output_file, text):
    p = Popen([
        'scripts/create-comm.py',
        '--annotation-level', 'section',
        'tests/testdata/les-deux-chandeliers.txt',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = it.next()
    assert comm.id == 'tests/testdata/les-deux-chandeliers.txt'
    assert validate_communication(comm)
    assert comm.text == text
    assert len(comm.sectionList) == 2

    try:
        it.next()
    except StopIteration:
        pass
    else:
        assert False
