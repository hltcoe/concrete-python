# -*- coding: utf-8 -*-


from __future__ import unicode_literals
from pytest import fixture, mark
from concrete.util import CommunicationReader
from concrete.validate import validate_communication
import os
import sys
from subprocess import Popen, PIPE


@fixture
def text():
    return '''\
Madame Magloire comprit, et elle alla chercher sur la cheminée de la \
chambre à coucher de monseigneur les deux chandeliers d'argent \
qu'elle posa sur la table tout allumés.\
''' + os.linesep + os.linesep + '''\
—Monsieur le curé, dit l'homme, vous êtes bon. Vous ne me méprisez \
pas. Vous me recevez chez vous. Vous allumez vos cierges pour moi. \
Je ne vous ai pourtant pas caché d'où je viens et que je suis un homme \
malheureux.\
''' + os.linesep


@fixture
def output_file(tmpdir):
    yield str(tmpdir / 'output.comm')


def test_create_comm(output_file, text):
    p = Popen([
        sys.executable,
        'scripts/create-comm.py',
        'tests/testdata/les-deux-chandeliers.txt',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = next(it)
    assert comm.id == 'tests/testdata/les-deux-chandeliers.txt'
    assert validate_communication(comm)
    assert comm.text == text
    assert comm.sectionList is None

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False


@mark.posix
def test_create_comm_stdin(output_file, text):
    p = Popen([
        sys.executable,
        'scripts/create-comm.py',
        '-',
        output_file
    ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    with open('tests/testdata/les-deux-chandeliers.txt', 'rb') as f:
        (stdout, stderr) = p.communicate(f.read())
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = next(it)
    assert comm.id == '/dev/fd/0'
    assert validate_communication(comm)
    assert comm.text == text
    assert comm.sectionList is None

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False


@mark.posix
def test_create_comm_stdout(output_file, text):
    p = Popen([
        sys.executable,
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

    (comm, _) = next(it)
    assert comm.id == 'tests/testdata/les-deux-chandeliers.txt'
    assert validate_communication(comm)
    assert comm.text == text
    assert comm.sectionList is None

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False


def test_create_comm_annotated(output_file, text):
    p = Popen([
        sys.executable,
        'scripts/create-comm.py',
        '--annotation-level', 'section',
        'tests/testdata/les-deux-chandeliers.txt',
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert p.returncode == 0

    reader = CommunicationReader(output_file)
    it = iter(reader)

    (comm, _) = next(it)
    assert comm.id == 'tests/testdata/les-deux-chandeliers.txt'
    assert validate_communication(comm)
    assert comm.text == text
    assert len(comm.sectionList) == 2

    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False
