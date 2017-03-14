# -*- coding: utf-8 -*-


from __future__ import unicode_literals
from pytest import fixture, mark
import io
import os
import sys
import json
from subprocess import Popen, PIPE
from tempfile import mkstemp


SERIF_TEXT = '''\
<DOC id="dog-bites-man" type="other">
<HEADLINE>
Dog Bites Man
</HEADLINE>
<TEXT>
<P>
John Smith, manager of ACMÉ INC, was bit by a dog on March 10th, 2013.
</P>
<P>
He died!
</P>
<P>
John's daughter Mary expressed sorrow.
</P>
</TEXT>
</DOC>
'''

LES_DEUX_TEXT = '''\
Madame Magloire comprit, et elle alla chercher sur la cheminée de la \
chambre à coucher de monseigneur les deux chandeliers d'argent \
qu'elle posa sur la table tout allumés.

—Monsieur le curé, dit l'homme, vous êtes bon. Vous ne me méprisez \
pas. Vous me recevez chez vous. Vous allumez vos cierges pour moi. \
Je ne vous ai pourtant pas caché d'où je viens et que je suis un homme \
malheureux.
'''


def assert_json_protocol_ok(json_path, expected_text):
    with io.open(json_path, encoding='utf-8') as f:
        json_obj = json.load(f)
        assert json_obj['4']['str'] == expected_text


def assert_simple_json_protocol_ok(json_path, expected_text):
    with io.open(json_path, encoding='utf-8') as f:
        json_obj = json.load(f)
        assert json_obj['text'] == expected_text


@fixture
def output_file(request):
    (fd, path) = mkstemp()
    os.close(fd)

    def _remove():
        if os.path.exists(path):
            os.remove(path)

    request.addfinalizer(_remove)
    return path


@mark.parametrize('args,text,assertion', [
    (['tests/testdata/les-deux-chandeliers.concrete'],
     LES_DEUX_TEXT, assert_simple_json_protocol_ok),
    (['--protocol', 'simple', 'tests/testdata/les-deux-chandeliers.concrete'],
     LES_DEUX_TEXT, assert_simple_json_protocol_ok),
    (['--protocol', 'TJSONProtocol', 'tests/testdata/les-deux-chandeliers.concrete'],
     LES_DEUX_TEXT, assert_json_protocol_ok),
    (['tests/testdata/serif_dog-bites-man.concrete'],
     SERIF_TEXT, assert_simple_json_protocol_ok),
    (['--protocol', 'simple', 'tests/testdata/serif_dog-bites-man.concrete'],
     SERIF_TEXT, assert_simple_json_protocol_ok),
    (['--protocol', 'TJSONProtocol', 'tests/testdata/serif_dog-bites-man.concrete'],
     SERIF_TEXT, assert_json_protocol_ok),
])
def test_concrete2json(output_file, args, text, assertion):
    p = Popen([
        sys.executable,
        'scripts/concrete2json.py',
    ] + args + [
        output_file
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    assert stdout == b''
    assert stderr == b''
    assert p.returncode == 0

    assertion(output_file, text)
