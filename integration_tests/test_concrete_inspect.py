import unittest

from concrete import AnnotationMetadata, Communication
import concrete.inspect
from concrete.validate import validate_communication

import sys
from subprocess import Popen, PIPE


class TestConcreteInspect(unittest.TestCase):
    def setUp(self):
        self.comm_path = "tests/testdata/serif_dog-bites-man.concrete"

    def test_print_conll_style_tags_for_communication(self):
        p = Popen([
            sys.executable, 'scripts/concrete_inspect.py',
            '--char-offsets', '--dependency', '--lemmas', '--ner', '--pos',
            self.comm_path
        ], stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = p.communicate()
        expected_output = '''\
INDEX	TOKEN	CHAR	LEMMA	POS	NER	HEAD
-----	-----	----	-----	---	---	----
1	John	John		NNP	PER	
2	Smith	Smith		NNP	PER	
3	,	,		,		
4	manager	manager		NN		
5	of	of		IN		
6	ACME	ACME		NNP	ORG	
7	INC	INC		NNP	ORG	
8	,	,		,		
9	was	was		VBD		
10	bit	bit		NN		
11	by	by		IN		
12	a	a		DT		
13	dog	dog		NN		
14	on	on		IN		
15	March	March		DATE-NNP		
16	10th	10th		JJ		
17	,	,		,		
18	2013	2013		CD		
19	.	.		.		

1	He	He		PRP		
2	died	died		VBD		
3	!	!		.		

1	John	John		NNP	PER	
2	's	's		POS		
3	daughter	daughter		NN		
4	Mary	Mary		NNP	PER	
5	expressed	expressed		VBD		
6	sorrow	sorrow		NN		
7	.	.		.		

'''
        self.assertEquals(0, p.returncode)
        self.assertEquals(expected_output, stdout)
        self.assertEquals('', stderr)

    def test_print_entities(self):
        p = Popen([
            sys.executable, 'scripts/concrete_inspect.py',
            '--entities',
            self.comm_path
        ], stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = p.communicate()
        expected_output = '''\
Entity Set 0 (Serif: doc-entities):
  Entity 0-0:
      EntityMention 0-0-0:
          tokens:     John Smith
          text:       John Smith
          entityType: PER
          phraseType: PhraseType.NAME
      EntityMention 0-0-1:
          tokens:     John Smith , manager of ACME INC ,
          text:       John Smith, manager of ACME INC,
          entityType: PER
          phraseType: PhraseType.APPOSITIVE
      EntityMention 0-0-2:
          tokens:     manager of ACME INC
          text:       manager of ACME INC
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
          tokens:     ACME INC
          text:       ACME INC
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


Entity Set 1 (Serif: doc-values):
  Entity 1-0:
      EntityMention 1-0-0:
          tokens:     March 10th , 2013
          text:       March 10th, 2013
          entityType: TIMEX2.TIME
          phraseType: PhraseType.OTHER


'''
        self.assertEquals(0, p.returncode)
        self.assertEquals(expected_output, stdout)
        self.assertEquals('', stderr)

    def test_print_situation_mentions(self):
        p = Popen([
            sys.executable, 'scripts/concrete_inspect.py',
            '--situation-mentions',
            self.comm_path
        ], stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = p.communicate()
        expected_output = '''\
Situation Set 0 (Serif: relations):
  SituationMention 0-0:
          situationType:      ORG-AFF.Employment
          Argument 0:
              role:           Role.RELATION_SOURCE_ROLE
              entityMention:  manager of ACME INC
          Argument 1:
              role:           Role.RELATION_TARGET_ROLE
              entityMention:  ACME INC

  SituationMention 0-1:
          situationType:      PER-SOC.Family
          Argument 0:
              role:           Role.RELATION_SOURCE_ROLE
              entityMention:  John
          Argument 1:
              role:           Role.RELATION_TARGET_ROLE
              entityMention:  daughter


Situation Set 1 (Serif: events):
  SituationMention 1-0:
          text:               died
          situationType:      Life.Die
          Argument 0:
              role:           Victim
              entityMention:  He


'''
        self.assertEquals(0, p.returncode)
        self.assertEquals(expected_output, stdout)
        self.assertEquals('', stderr)

    def test_print_situations(self):
        p = Popen([
            sys.executable, 'scripts/concrete_inspect.py',
            '--situations',
            self.comm_path
        ], stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = p.communicate()
        expected_output = '''\
Situation Set 0 (Serif: relations):

Situation Set 1 (Serif: events):
  Situation 1-0:
      situationType:    Life.Die


'''
        self.assertEquals(0, p.returncode)
        self.assertEquals(expected_output, stdout)
        self.assertEquals('', stderr)

    def test_print_text_for_communication(self):
        p = Popen([
            sys.executable, 'scripts/concrete_inspect.py',
            '--text',
            self.comm_path
        ], stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = p.communicate()
        expected_output = '''\
<DOC id="dog-bites-man" type="other">
<HEADLINE>
Dog Bites Man
</HEADLINE>
<TEXT>
<P>
John Smith, manager of ACME INC, was bit by a dog on March 10th, 2013.
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
        self.assertEquals(0, p.returncode)
        self.assertEquals(expected_output, stdout)
        self.assertEquals('', stderr)

    def test_print_tokens_with_entityMentions(self):
        p = Popen([
            sys.executable, 'scripts/concrete_inspect.py',
            '--mentions',
            self.comm_path
        ], stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = p.communicate()
        expected_output = '''
<ENTITY ID=0><ENTITY ID=0>John Smith</ENTITY> , <ENTITY ID=0>manager of <ENTITY ID=1>ACME INC</ENTITY></ENTITY> ,</ENTITY> was bit by a dog on <ENTITY ID=3>March 10th , 2013</ENTITY> .

<ENTITY ID=0>He</ENTITY> died !

<ENTITY ID=2><ENTITY ID=0>John</ENTITY> 's <ENTITY ID=2>daughter</ENTITY> Mary</ENTITY> expressed sorrow .

'''
        self.assertEquals(0, p.returncode)
        self.assertEquals(expected_output, stdout)
        self.assertEquals('', stderr)

    def test_print_tokens_for_communication(self):
        p = Popen([
            sys.executable, 'scripts/concrete_inspect.py',
            '--tokens',
            self.comm_path
        ], stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = p.communicate()
        expected_output = '''
John Smith , manager of ACME INC , was bit by a dog on March 10th , 2013 .

He died !

John 's daughter Mary expressed sorrow .

'''
        self.assertEquals(0, p.returncode)
        self.assertEquals(expected_output, stdout)
        self.assertEquals('', stderr)

    def test_print_penn_treebank_for_communication(self):
        p = Popen([
            sys.executable, 'scripts/concrete_inspect.py',
            '--treebank',
            self.comm_path
        ], stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = p.communicate()
        expected_output = '''\
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


'''
        self.assertEquals(0, p.returncode)
        self.assertEquals(expected_output, stdout)
        self.assertEquals('', stderr)
