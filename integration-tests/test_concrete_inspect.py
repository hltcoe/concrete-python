# -*- coding: utf-8 -*-


import sys
from pytest import fixture, mark
from subprocess import Popen, PIPE


@fixture
def comm_path(request):
    return 'tests/testdata/serif_dog-bites-man.concrete'


@fixture
def comms_path(request):
    return 'tests/testdata/serif_les-deux_concatenated.concrete'


@fixture
def comms_tgz_path(request):
    return 'tests/testdata/serif_les-deux.tar.gz'


@mark.parametrize('which,args,output_prefix', [
    (range(8), (), ''),
    (range(8), ('--annotation-headers',), '\nconll\n-----\n'),
    ((0, 1, 2), ('--tool', 'fake'), ''),
    ((0, 1, 2), ('--tool', 'fake', '--annotation-headers',), '\nconll\n-----\n'),
    ((0, 1, 2, 4), ('--tool', 'Serif: part-of-speech'), ''),
    ((0, 1, 2, 4), ('--tool', 'Serif: part-of-speech', '--annotation-headers',), '\nconll\n-----\n'),
    ((0, 1, 2, 5), ('--tool', 'Serif: names'), ''),
    ((0, 1, 2, 5), ('--tool', 'Serif: names', '--annotation-headers',), '\nconll\n-----\n'),
    ((0, 1, 2, 6, 7), ('--tool', 'Stanford'), ''),
    ((0, 1, 2, 6, 7), ('--tool', 'Stanford', '--annotation-headers',), '\nconll\n-----\n'),
])
def test_print_conll_style_tags_for_communication(comm_path, which, args,
                                                  output_prefix):
    p = Popen([
        sys.executable, 'scripts/concrete_inspect.py',
        '--char-offsets',
        '--dependency',
        '--lemmas',
        '--ner',
        '--pos',
    ] + list(args) + [
        comm_path
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    expected_output = output_prefix + '''\
INDEX\tTOKEN\tCHAR\tLEMMA\tPOS\tNER\tHEAD\tDEPREL
-----\t-----\t----\t-----\t---\t---\t----\t------
''' + u'\n'.join(
        u'\t'.join((w if i in which else '') for (i, w) in enumerate(row))
        for row in (
            ('1', 'John', 'John', '', 'NNP', 'PER', '2', 'compound'),
            ('2', 'Smith', 'Smith', '', 'NNP', 'PER', '10', 'nsubjpass'),
            ('3', ',', ',', '', ',', '', '', ''),
            ('4', 'manager', 'manager', '', 'NN', '', '2', 'appos'),
            ('5', 'of', 'of', '', 'IN', '', '7', 'case'),
            ('6', u'ACMÉ', u'ACMÉ', '', 'NNP', 'ORG', '7', 'compound'),
            ('7', 'INC', 'INC', '', 'NNP', 'ORG', '4', 'nmod'),
            ('8', ',', ',', '', ',', '', '', ''),
            ('9', 'was', 'was', '', 'VBD', '', '10', 'auxpass'),
            ('10', 'bit', 'bit', '', 'NN', '', '0', 'ROOT'),
            ('11', 'by', 'by', '', 'IN', '', '13', 'case'),
            ('12', 'a', 'a', '', 'DT', '', '13', 'det'),
            ('13', 'dog', 'dog', '', 'NN', '', '10', 'nmod'),
            ('14', 'on', 'on', '', 'IN', '', '15', 'case'),
            ('15', 'March', 'March', '', 'DATE-NNP', '', '13', 'nmod'),
            ('16', '10th', '10th', '', 'JJ', '', '15', 'amod'),
            ('17', ',', ',', '', ',', '', '', ''),
            ('18', '2013', '2013', '', 'CD', '', '13', 'amod'),
            ('19', '.', '.', '', '.', '', '', ''),
            (),
            ('1', 'He', 'He', '', 'PRP', '', '2', 'nsubj'),
            ('2', 'died', 'died', '', 'VBD', '', '0', 'ROOT'),
            ('3', '!', '!', '', '.', '', '', ''),
            (),
            ('1', 'John', 'John', '', 'NNP', 'PER', '3', 'nmod:poss'),
            ('2', '\'s', '\'s', '', 'POS', '', '1', 'case'),
            ('3', 'daughter', 'daughter', '', 'NN', '', '5', 'dep'),
            ('4', 'Mary', 'Mary', '', 'NNP', 'PER', '5', 'nsubj'),
            ('5', 'expressed', 'expressed', '', 'VBD', '', '0', 'ROOT'),
            ('6', 'sorrow', 'sorrow', '', 'NN', '', '5', 'dobj'),
            ('7', '.', '.', '', '.', '', '', ''),
            (),
        )
    ).encode('utf-8') + '\n'
    assert '' == stderr
    assert expected_output == stdout
    assert 0 == p.returncode


@mark.parametrize('first,second,args,output_prefix', [
    (True, True, (), ''),
    (True, True, ('--annotation-headers',), '\nentities\n--------\n'),
    (True, False, ('--tool', 'Serif: doc-entities'), ''),
    (True, False, ('--tool', 'Serif: doc-entities', '--annotation-headers',), '\nentities\n--------\n'),
    (False, True, ('--tool', 'Serif: doc-values'), ''),
    (False, True, ('--tool', 'Serif: doc-values', '--annotation-headers',), '\nentities\n--------\n'),
])
def test_print_entities(comm_path, first, second, args, output_prefix):
    p = Popen([
        sys.executable, 'scripts/concrete_inspect.py',
        '--entities',
    ] + list(args) + [
        comm_path
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    expected_output = output_prefix
    if first:
        expected_output += u'''\
Entity Set 0 (Serif: doc-entities):
  Entity 0-0:
      EntityMention 0-0-0:
          tokens:     John Smith
          text:       John Smith
          entityType: PER
          phraseType: PhraseType.NAME
      EntityMention 0-0-1:
          tokens:     John Smith , manager of ACMÉ INC ,
          text:       John Smith, manager of ACMÉ INC,
          entityType: PER
          phraseType: PhraseType.APPOSITIVE
      EntityMention 0-0-2:
          tokens:     manager of ACMÉ INC
          text:       manager of ACMÉ INC
          entityType: PER
          phraseType: PhraseType.COMMON_NOUN
      EntityMention 0-0-3:
          tokens:     He
          text:       He
          entityType: PER
          phraseType: PhraseType.PRONOUN
      EntityMention 0-0-4:
          tokens:     John
          text:       John
          entityType: PER.Individual
          phraseType: PhraseType.NAME

  Entity 0-1:
      EntityMention 0-1-0:
          tokens:     ACMÉ INC
          text:       ACMÉ INC
          entityType: ORG
          phraseType: PhraseType.NAME

  Entity 0-2:
      EntityMention 0-2-0:
          tokens:     John 's daughter Mary
          text:       John's daughter Mary
          entityType: PER.Individual
          phraseType: PhraseType.NAME
      EntityMention 0-2-1:
          tokens:     daughter
          text:       daughter
          entityType: PER
          phraseType: PhraseType.COMMON_NOUN


'''.encode('utf-8')
    if second:
        expected_output += u'''\
Entity Set 1 (Serif: doc-values):
  Entity 1-0:
      EntityMention 1-0-0:
          tokens:     March 10th , 2013
          text:       March 10th, 2013
          entityType: TIMEX2.TIME
          phraseType: PhraseType.OTHER


'''.encode('utf-8')
    assert '' == stderr
    assert expected_output == stdout
    assert 0 == p.returncode


@mark.parametrize('first,second,args,output_prefix', [
    (True, True, (), ''),
    (True, True, ('--annotation-headers',), '\nsituation mentions\n------------------\n'),
    (True, False, ('--tool', 'Serif: relations'), ''),
    (True, False, ('--tool', 'Serif: relations', '--annotation-headers',), '\nsituation mentions\n------------------\n'),
    (False, True, ('--tool', 'Serif: events'), ''),
    (False, True, ('--tool', 'Serif: events', '--annotation-headers',), '\nsituation mentions\n------------------\n'),
])
def test_print_situation_mentions(comm_path, first, second, args, output_prefix):
    p = Popen([
        sys.executable, 'scripts/concrete_inspect.py',
        '--situation-mentions',
    ] + list(args) + [
        comm_path
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    expected_output = output_prefix
    if first:
        expected_output += u'''\
Situation Set 0 (Serif: relations):
  SituationMention 0-0:
          situationType:      ORG-AFF.Employment
          Argument 0:
              role:           Role.RELATION_SOURCE_ROLE
              entityMention:  manager of ACMÉ INC
          Argument 1:
              role:           Role.RELATION_TARGET_ROLE
              entityMention:  ACMÉ INC

  SituationMention 0-1:
          situationType:      PER-SOC.Family
          Argument 0:
              role:           Role.RELATION_SOURCE_ROLE
              entityMention:  John
          Argument 1:
              role:           Role.RELATION_TARGET_ROLE
              entityMention:  daughter


'''.encode('utf-8')
    if second:
        expected_output += u'''\
Situation Set 1 (Serif: events):
  SituationMention 1-0:
          text:               died
          situationType:      Life.Die
          Argument 0:
              role:           Victim
              entityMention:  He


'''.encode('utf-8')
    assert '' == stderr
    assert expected_output == stdout
    assert 0 == p.returncode


@mark.parametrize('first,second,args,output_prefix', [
    (True, True, (), ''),
    (True, True, ('--annotation-headers',), '\nsituations\n----------\n'),
    (True, False, ('--tool', 'Serif: relations'), ''),
    (True, False, ('--tool', 'Serif: relations', '--annotation-headers',), '\nsituations\n----------\n'),
    (False, True, ('--tool', 'Serif: events'), ''),
    (False, True, ('--tool', 'Serif: events', '--annotation-headers',), '\nsituations\n----------\n'),
])
def test_print_situations(comm_path, first, second, args, output_prefix):
    p = Popen([
        sys.executable, 'scripts/concrete_inspect.py',
        '--situations',
    ] + list(args) + [
        comm_path
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    expected_output = output_prefix
    if first:
        expected_output += u'''\
Situation Set 0 (Serif: relations):

'''.encode('utf-8')
    if second:
        expected_output += u'''\
Situation Set 1 (Serif: events):
  Situation 1-0:
      situationType:    Life.Die


'''.encode('utf-8')
    assert '' == stderr
    assert expected_output == stdout
    assert 0 == p.returncode


@mark.parametrize('args,output_prefix', [
    ((), ''),
    (('--annotation-headers',), '\ntext\n----\n'),
    (('--tool', 'concrete_serif v3.10.1pre'), ''),
    (('--tool', 'concrete_serif v3.10.1pre', '--annotation-headers',), '\ntext\n----\n'),
])
def test_print_text_for_communication(comm_path, args, output_prefix):
    p = Popen([
        sys.executable, 'scripts/concrete_inspect.py',
        '--text',
    ] + list(args) + [
        comm_path
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    expected_output = output_prefix + u'''\
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

'''.encode('utf-8')
    assert '' == stderr
    assert expected_output == stdout
    assert 0 == p.returncode


@mark.parametrize('first,second,third,args,output_prefix', [
    (True, True, True, (), ''),
    (True, True, True, ('--annotation-headers',), '\nmentions\n--------\n'),
    (True, False, False, ('--tool', 'Serif: names'), ''),
    (True, False, False, ('--tool', 'Serif: names', '--annotation-headers',), '\nmentions\n--------\n'),
    (False, True, False, ('--tool', 'Serif: values'), ''),
    (False, True, False, ('--tool', 'Serif: values', '--annotation-headers',), '\nmentions\n--------\n'),
    (False, False, True, ('--tool', 'Serif: mentions'), ''),
    (False, False, True, ('--tool', 'Serif: mentions', '--annotation-headers',), '\nmentions\n--------\n'),
])
def test_print_tokens_with_entityMentions(comm_path, first, second, third,
                                          args, output_prefix):
    p = Popen([
        sys.executable, 'scripts/concrete_inspect.py',
        '--mentions',
    ] + list(args) + [
        comm_path
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    if third:
        expected_output = output_prefix + u'''
<ENTITY ID=0><ENTITY ID=0>John Smith</ENTITY> , <ENTITY ID=0>manager of \
<ENTITY ID=1>ACMÉ INC</ENTITY></ENTITY> ,</ENTITY> was bit by a dog on \
%sMarch 10th , 2013%s .

<ENTITY ID=0>He</ENTITY> died !

<ENTITY ID=2><ENTITY ID=0>John</ENTITY> 's <ENTITY ID=2>daughter</ENTITY> \
Mary</ENTITY> expressed sorrow .

'''.encode('utf-8')
    else:
        expected_output = output_prefix + u'''
John Smith , manager of \
ACMÉ INC , was bit by a dog on \
%sMarch 10th , 2013%s .

He died !

John 's daughter \
Mary expressed sorrow .

'''.encode('utf-8')
    expected_output = expected_output % (
        '<ENTITY ID=3>' if second else '',
        '</ENTITY>' if second else '')
    assert '' == stderr
    assert expected_output == stdout
    assert 0 == p.returncode


@mark.parametrize('args,output_prefix', [
    ((), ''),
    (('--annotation-headers',), '\ntokens\n------\n'),
    (('--tool', 'Serif: tokens',), ''),
    (('--tool', 'Serif: tokens', '--annotation-headers',), '\ntokens\n------\n'),
])
def test_print_tokens_for_communication(comm_path, args, output_prefix):
    p = Popen([
        sys.executable, 'scripts/concrete_inspect.py',
        '--tokens',
    ] + list(args) + [
        comm_path
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    expected_output = output_prefix + u'''
John Smith , manager of ACMÉ INC , was bit by a dog on March 10th , 2013 .

He died !

John 's daughter Mary expressed sorrow .

'''.encode('utf-8')
    assert '' == stderr
    assert expected_output == stdout
    assert 0 == p.returncode


@mark.parametrize('args,output_prefix', [
    ((), ''),
    (('--annotation-headers',), '\ntreebank\n--------\n'),
    (('--tool', 'Serif: parse',), ''),
    (('--tool', 'Serif: parse', '--annotation-headers',), '\ntreebank\n--------\n'),
])
def test_print_penn_treebank_for_communication(comm_path, args, output_prefix):
    p = Popen([
        sys.executable, 'scripts/concrete_inspect.py',
        '--treebank',
    ] + list(args) + [
        comm_path
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    expected_output = output_prefix + u'''\
(S (NP (NPP (NNP john)
            (NNP smith))
       (, ,)
       (NP (NPA (NN manager))
           (PP (IN of)
               (NPP (NNP acme)
                    (NNP inc))))
       (, ,))
   (VP (VBD was)
       (NP (NPA (NN bit))
           (PP (IN by)
               (NP (NPA (DT a)
                        (NN dog))
                   (PP (IN on)
                       (NP (DATE (DATE-NNP march)
                                 (JJ 10th))
                           (, ,)
                           (NPA (CD 2013))))))))
   (. .))


(S (NPA (PRP he))
   (VP (VBD died))
   (. !))


(S (NPA (NPPOS (NPP (NNP john))
               (POS 's))
        (NN daughter)
        (NPP (NNP mary)))
   (VP (VBD expressed)
       (NPA (NN sorrow)))
   (. .))


'''.encode('utf-8')
    assert '' == stderr
    assert expected_output == stdout
    assert 0 == p.returncode


@mark.parametrize('which,args,output_prefix', [
    (range(15), (), ''),
    (range(15), ('--annotation-headers',), '\nmetadata\n--------\n'),
    ((0,), ('--tool', 'concrete_serif v3.10.1pre'), ''),
    ((0,), ('--tool', 'concrete_serif v3.10.1pre', '--annotation-headers',), '\nmetadata\n--------\n'),
    ((1,), ('--tool', 'Serif: tokens'), ''),
    ((1,), ('--tool', 'Serif: tokens', '--annotation-headers',), '\nmetadata\n--------\n'),
    ((2,), ('--tool', 'Stanford'), ''),
    ((2,), ('--tool', 'Stanford', '--annotation-headers',), '\nmetadata\n--------\n'),
    ((3,), ('--tool', 'Serif: parse'), ''),
    ((3,), ('--tool', 'Serif: parse', '--annotation-headers',), '\nmetadata\n--------\n'),
    ((4, 6), ('--tool', 'Serif: names'), ''),
    ((4, 6), ('--tool', 'Serif: names', '--annotation-headers',), '\nmetadata\n--------\n'),
    ((5,), ('--tool', 'Serif: part-of-speech'), ''),
    ((5,), ('--tool', 'Serif: part-of-speech', '--annotation-headers',), '\nmetadata\n--------\n'),
    ((7,), ('--tool', 'Serif: values'), ''),
    ((7,), ('--tool', 'Serif: values', '--annotation-headers',), '\nmetadata\n--------\n'),
    ((8,), ('--tool', 'Serif: mentions'), ''),
    ((8,), ('--tool', 'Serif: mentions', '--annotation-headers',), '\nmetadata\n--------\n'),
    ((9,), ('--tool', 'Serif: doc-entities'), ''),
    ((9,), ('--tool', 'Serif: doc-entities', '--annotation-headers',), '\nmetadata\n--------\n'),
    ((10,), ('--tool', 'Serif: doc-values'), ''),
    ((10,), ('--tool', 'Serif: doc-values', '--annotation-headers',), '\nmetadata\n--------\n'),
    ((11, 13), ('--tool', 'Serif: relations'), ''),
    ((11, 13), ('--tool', 'Serif: relations', '--annotation-headers',), '\nmetadata\n--------\n'),
    ((12, 14), ('--tool', 'Serif: events'), ''),
    ((12, 14), ('--tool', 'Serif: events', '--annotation-headers',), '\nmetadata\n--------\n'),
])
def test_print_metadata_for_communication(comm_path, which, args, output_prefix):
    p = Popen([
        sys.executable, 'scripts/concrete_inspect.py',
        '--metadata',
    ] + list(args) + [
        comm_path
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    expected_output = output_prefix
    if 0 in which:
        expected_output += u'Communication:  concrete_serif v3.10.1pre\n'
        expected_output += '\n'
    if 1 in which:
        expected_output += '  Tokenization:  Serif: tokens\n'
        expected_output += '\n'
    if 2 in which:
        expected_output += '    Dependency Parse:  Stanford\n'
        expected_output += '\n'
    if 3 in which:
        expected_output += '    Parse:  Serif: parse\n'
        expected_output += '\n'
    if 4 in which:
        expected_output += '    TokenTagging:  Serif: names\n'
    if 5 in which:
        expected_output += '    TokenTagging:  Serif: part-of-speech\n'
    if 4 in which or 5 in which:
        expected_output += '\n'
    if 6 in which:
        expected_output += '  EntityMentionSet #0:  Serif: names\n'
    if 7 in which:
        expected_output += '  EntityMentionSet #1:  Serif: values\n'
    if 8 in which:
        expected_output += '  EntityMentionSet #2:  Serif: mentions\n'
    expected_output += '\n'
    if 9 in which:
        expected_output += '  EntitySet #0:  Serif: doc-entities\n'
    if 10 in which:
        expected_output += '  EntitySet #1:  Serif: doc-values\n'
    expected_output += '\n'
    if 11 in which:
        expected_output += '  SituationMentionSet #0:  Serif: relations\n'
    if 12 in which:
        expected_output += '  SituationMentionSet #1:  Serif: events\n'
    expected_output += '\n'
    if 13 in which:
        expected_output += '  SituationSet #0:  Serif: relations\n'
    if 14 in which:
        expected_output += '  SituationSet #1:  Serif: events\n'
    expected_output += '\n'
    assert '' == stderr
    assert expected_output == stdout
    assert 0 == p.returncode


@mark.parametrize('args,output_prefix', [
    ((), ''),
    (('--annotation-headers',), '\nsections\n--------\n'),
    (('--tool', 'concrete_serif v3.10.1pre',), ''),
    (('--tool', 'concrete_serif v3.10.1pre', '--annotation-headers',), '\nsections\n--------\n'),
])
def test_print_sections_for_communication(comm_path, args, output_prefix):
    p = Popen([
        sys.executable, 'scripts/concrete_inspect.py',
        '--sections',
    ] + list(args) + [
        comm_path
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    expected_output = output_prefix + u'''\
Section 0 (0ab68635-c83d-4b02-b8c3-288626968e05), from 81 to 82:



Section 1 (54902d75-1841-4d8d-b4c5-390d4ef1a47a), from 85 to 162:

John Smith, manager of ACMÉ INC, was bit by a dog on March 10th, 2013.
</P>


Section 2 (7ec8b7d9-6be0-4c62-af57-3c6c48bad711), from 165 to 180:

He died!
</P>


Section 3 (68da91a1-5beb-4129-943d-170c40c7d0f7), from 183 to 228:

John's daughter Mary expressed sorrow.
</P>



'''.encode('utf-8')
    assert '' == stderr
    assert expected_output == stdout
    assert 0 == p.returncode


@mark.parametrize('args,output_prefix', [
    ((), ''),
    (('--annotation-headers',), '\nid\n--\n'),
    (('--tool', 'concrete_serif v3.10.1pre'), ''),
    (('--tool', 'concrete_serif v3.10.1pre', '--annotation-headers',), '\nid\n--\n'),
])
def test_print_id_for_communication(comm_path, args, output_prefix):
    p = Popen([
        sys.executable, 'scripts/concrete_inspect.py',
        '--id',
    ] + list(args) + [
        comm_path
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    expected_output = output_prefix + u'''\
tests/testdata/serif_dog-bites-man.xml
'''.encode('utf-8')
    assert '' == stderr
    assert expected_output == stdout
    assert 0 == p.returncode


@mark.parametrize('first,second,args,output_prefix', [
    (True, True, (), ''),
    (True, True, ('--annotation-headers',), '\ntext\n----\n'),
    (True, False, ('--tool', 'concrete_serif v3.10.1pre'), ''),
    (True, False, ('--tool', 'concrete_serif v3.10.1pre', '--annotation-headers',), '\ntext\n----\n'),
])
def test_print_multiple_communications(comms_path, first, second, args,
                                       output_prefix):
    p = Popen([
        sys.executable, 'scripts/concrete_inspect.py',
        '--text',
    ] + list(args) + [
        comms_path
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    expected_output = output_prefix
    if first:
        expected_output += u'''\
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

'''.encode('utf-8')
    expected_output += output_prefix
    if second:
        expected_output += u'''\
Madame Magloire comprit, et elle alla chercher sur la cheminée de la \
chambre à coucher de monseigneur les deux chandeliers d'argent \
qu'elle posa sur la table tout allumés.

—Monsieur le curé, dit l'homme, vous êtes bon. Vous ne me méprisez \
pas. Vous me recevez chez vous. Vous allumez vos cierges pour moi. \
Je ne vous ai pourtant pas caché d'où je viens et que je suis un homme \
malheureux.

'''.encode('utf-8')
    assert '' == stderr
    assert expected_output == stdout
    assert 0 == p.returncode


@mark.parametrize('first,second,args,output_prefix', [
    (True, True, (), ''),
    (True, True, ('--annotation-headers',), '\ntext\n----\n'),
    (True, False, ('--tool', 'concrete_serif v3.10.1pre'), ''),
    (True, False, ('--tool', 'concrete_serif v3.10.1pre', '--annotation-headers',), '\ntext\n----\n'),
])
def test_print_multiple_communications_tgz(comms_tgz_path, first, second, args,
                                           output_prefix):
    p = Popen([
        sys.executable, 'scripts/concrete_inspect.py',
        '--text',
    ] + list(args) + [
        comms_tgz_path
    ], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    expected_output = output_prefix
    if first:
        expected_output += u'''\
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

'''.encode('utf-8')
    expected_output += output_prefix
    if second:
        expected_output += u'''\
Madame Magloire comprit, et elle alla chercher sur la cheminée de la \
chambre à coucher de monseigneur les deux chandeliers d'argent \
qu'elle posa sur la table tout allumés.

—Monsieur le curé, dit l'homme, vous êtes bon. Vous ne me méprisez \
pas. Vous me recevez chez vous. Vous allumez vos cierges pour moi. \
Je ne vous ai pourtant pas caché d'où je viens et que je suis un homme \
malheureux.

'''.encode('utf-8')
    assert '' == stderr
    assert expected_output == stdout
    assert 0 == p.returncode
