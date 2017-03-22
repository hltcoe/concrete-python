from __future__ import unicode_literals
from __future__ import print_function

import sys

from concrete import (
    AnnotationMetadata,
    Communication,
    EntityMention,
    EntityMentionSet,
    MentionArgument,
    Property,
    Section,
    Sentence,
    SituationMention,
    SituationMentionSet,
    TextSpan,
    Token,
    TokenList,
    TokenRefSequence,
    Tokenization,
    TokenizationKind,
)

from concrete.inspect import print_situation_mentions
from concrete.util import generate_UUID as genId
from concrete.util.references import add_references_to_communication


def gen_comm(num_properties=0):
    ts = 17
    meta_tokn = AnnotationMetadata(tool='tokn-tool', timestamp=ts)
    toks = TokenList(tokenList=[Token(tokenIndex=0,
                                      text='text',
                                      textSpan=TextSpan(start=0,
                                                        ending=1))])
    tokn = Tokenization(uuid=genId(), metadata=meta_tokn,
                        kind=TokenizationKind.TOKEN_LIST,
                        tokenList=toks)
    sentence = Sentence(uuid=genId(), tokenization=tokn)
    section = Section(uuid=genId(), kind='kind', label='label',
                      sentenceList=[sentence])
    trfs = TokenRefSequence(tokenizationId=tokn.uuid,
                            tokenIndexList=[0],
                            anchorTokenIndex=0)
    em = EntityMention(uuid=genId(), entityType='entityType',
                       text='text', tokens=trfs)
    meta_ems = AnnotationMetadata(tool='ems-tool', timestamp=ts)
    ems = EntityMentionSet(uuid=genId(), metadata=meta_ems,
                           mentionList=[em])
    meta_prop = AnnotationMetadata(tool='Annotator1',
                                   timestamp=ts)
    props = list(
        Property(
            value=u"Property%d" % i,
            metadata=meta_prop,
            polarity=4.0) for i in range(num_properties))
    am = MentionArgument(role='role', entityMentionId=em.uuid,
                         propertyList=props)
    sm = SituationMention(uuid=genId(), text='text',
                          situationType='stiuationType',
                          situationKind='situationKind',
                          tokens=trfs, argumentList=[am])
    meta_sms = AnnotationMetadata(tool='sms-tool', timestamp=ts)
    sms = SituationMentionSet(uuid=genId(), metadata=meta_sms,
                              mentionList=[sm])
    meta_comm = AnnotationMetadata(tool='tool', timestamp=ts)
    comm = Communication(uuid=genId(), id='id', text='text',
                         type='type', metadata=meta_comm,
                         sectionList=[section],
                         situationMentionSetList=[sms],
                         entityMentionSetList=[ems])
    add_references_to_communication(comm)
    return comm


class SimpleStringIO(object):

    def __init__(self):
        self.pieces = []

    def write(self, data):
        self.pieces.append(data)

    def getvalue(self):
        return u"".join(self.pieces)


def test_inspect_spr():
    # capture sys.stdout
    old_stdout = sys.stdout
    redirected_output = sys.stdout = SimpleStringIO()
    print_situation_mentions(gen_comm(0))
    sys.stdout = old_stdout
    assert 'Properties' not in redirected_output.getvalue()

    old_stdout = sys.stdout
    redirected_output = sys.stdout = SimpleStringIO()
    num_properties = 3
    print_situation_mentions(gen_comm(num_properties))
    sys.stdout = old_stdout
    assert 1 == redirected_output.getvalue().count(u"Properties")
    assert 1 == redirected_output.getvalue().count(u"Annotator1")
    assert num_properties == redirected_output.getvalue().count(u"Property")
    assert num_properties == redirected_output.getvalue().count(u"4.0")
