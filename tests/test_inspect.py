from __future__ import unicode_literals
from __future__ import print_function
import re

from pytest import mark
from mock import Mock, sentinel

from concrete.inspect import (
    _get_conll_tags_for_tokenization,
    print_situation_mentions,
    print_conll_style_tags_for_communication,
)
from concrete.util import generate_UUID, create_comm
from concrete.util.references import add_references_to_communication
from concrete import (
    AnnotationMetadata,
    Communication,
    Dependency,
    DependencyParse,
    EntityMention,
    EntityMentionSet,
    MentionArgument,
    Property,
    Section,
    Sentence,
    SituationMention,
    SituationMentionSet,
    TextSpan,
    TokenRefSequence,
    Tokenization,
    TokenizationKind,
    Token,
    TokenList,
    TokenTagging,
    TaggedToken,
)


def _comm_with_properties(num_properties):
    ts = 17
    meta_tokn = AnnotationMetadata(tool='tokn-tool', timestamp=ts)
    toks = TokenList(tokenList=[Token(tokenIndex=0,
                                      text='text',
                                      textSpan=TextSpan(start=0,
                                                        ending=1))])
    tokn = Tokenization(uuid=generate_UUID(), metadata=meta_tokn,
                        kind=TokenizationKind.TOKEN_LIST,
                        tokenList=toks)
    sentence = Sentence(uuid=generate_UUID(), tokenization=tokn)
    section = Section(uuid=generate_UUID(), kind='kind', label='label',
                      sentenceList=[sentence])
    trfs = TokenRefSequence(tokenizationId=tokn.uuid,
                            tokenIndexList=[0],
                            anchorTokenIndex=0)
    em = EntityMention(uuid=generate_UUID(), entityType='entityType',
                       text='text', tokens=trfs)
    meta_ems = AnnotationMetadata(tool='ems-tool', timestamp=ts)
    ems = EntityMentionSet(uuid=generate_UUID(), metadata=meta_ems,
                           mentionList=[em])
    meta_prop = AnnotationMetadata(tool='Annotator1',
                                   timestamp=ts)
    props = list(
        Property(
            value="Property%d" % i,
            metadata=meta_prop,
            polarity=4.0) for i in range(num_properties))
    am = MentionArgument(role='role', entityMentionId=em.uuid,
                         propertyList=props)
    sm = SituationMention(uuid=generate_UUID(),
                          tokens=trfs, argumentList=[am])
    meta_sms = AnnotationMetadata(tool='sms-tool', timestamp=ts)
    sms = SituationMentionSet(uuid=generate_UUID(), metadata=meta_sms,
                              mentionList=[sm])
    meta_comm = AnnotationMetadata(tool='tool', timestamp=ts)
    comm = Communication(uuid=generate_UUID(), id='id', text='text',
                         type='type', metadata=meta_comm,
                         sectionList=[section],
                         situationMentionSetList=[sms],
                         entityMentionSetList=[ems])
    add_references_to_communication(comm)
    return comm


def comm_with_other_tags(*additional_tagging_types):
    comm = create_comm('quick', '''\
The quick brown fox jumped
over the lazy dog .

Or did she ?
''')
    for section in comm.sectionList:
        for sentence in section.sentenceList:
            sentence.tokenization.tokenTaggingList = [
                TokenTagging(
                    uuid=generate_UUID(),
                    metadata=AnnotationMetadata(
                        tool=u'tool',
                        timestamp=1,
                    ),
                    taggingType=u'upper',
                    taggedTokenList=[
                        TaggedToken(
                            tokenIndex=token.tokenIndex,
                            tag=token.text.upper(),
                        )
                        for token in sentence.tokenization.tokenList.tokenList
                    ],
                ),
                TokenTagging(
                    uuid=generate_UUID(),
                    metadata=AnnotationMetadata(
                        tool=u'tool',
                        timestamp=1,
                    ),
                    taggingType=u'lower',
                    taggedTokenList=[
                        TaggedToken(
                            tokenIndex=token.tokenIndex,
                            tag=token.text.lower(),
                        )
                        for token in sentence.tokenization.tokenList.tokenList
                    ],
                ),
            ] + [
                TokenTagging(
                    uuid=generate_UUID(),
                    metadata=AnnotationMetadata(
                        tool=u'tool/{}'.format(i),
                        timestamp=1,
                    ),
                    taggingType=tagging_type,
                    taggedTokenList=[
                        TaggedToken(
                            tokenIndex=token.tokenIndex,
                            tag='{}_{}/{}'.format(tagging_type, token.tokenIndex, i),
                        )
                        for token in sentence.tokenization.tokenList.tokenList
                    ],
                )
                for (i, tagging_type) in enumerate(additional_tagging_types)
            ]
    return comm


def test_print_conll_other_tags_ignore_all(capsys):
    print_conll_style_tags_for_communication(
        comm_with_other_tags())
    (out, err) = capsys.readouterr()
    assert err == ''
    assert out.startswith(
        'INDEX\tTOKEN\n'
        '-----\t-----\n'
        '1\tThe\n'
        '2\tquick\n'
    )


def test_print_conll_other_tags_ignore_some(capsys):
    print_conll_style_tags_for_communication(
        comm_with_other_tags(), other_tags=dict(upper=None))
    (out, err) = capsys.readouterr()
    assert err == ''
    assert out.startswith(
        'INDEX\tTOKEN\tupper\n'
        '-----\t-----\t-----\n'
        '1\tThe\tTHE\n'
        '2\tquick\tQUICK\n'
    )
    assert '3\tshe\tSHE\n' in out


def test_print_conll_other_tags(capsys):
    print_conll_style_tags_for_communication(
        comm_with_other_tags(), other_tags=dict(upper=None, lower=None))
    (out, err) = capsys.readouterr()
    assert err == ''
    assert (
        out.startswith(
            'INDEX\tTOKEN\tupper\tlower\n'
            '-----\t-----\t-----\t-----\n'
            '1\tThe\tTHE\tthe\n'
            '2\tquick\tQUICK\tquick\n'
        ) and '3\tshe\tSHE\tshe\n' in out
    ) or (
        out.startswith(
            'INDEX\tTOKEN\tlower\tupper\n'
            '-----\t-----\t-----\t-----\n'
            '1\tThe\tthe\tTHE\n'
            '2\tquick\tquick\tQUICK\n'
        ) and '3\tshe\tshe\tSHE\n' in out
    )


def test_print_conll_other_tags_repeated_other_tag(capsys):
    print_conll_style_tags_for_communication(
        comm_with_other_tags('upper', 'ner'),
        ner=True,
        other_tags=dict(upper=None))
    (out, err) = capsys.readouterr()
    assert err == ''
    assert out.startswith(
        'INDEX\tTOKEN\tNER\tupper\tupper\n'
        '-----\t-----\t---\t-----\t-----\n'
        '1\tThe\tner_0/1\tTHE\tupper_0/0\n'
        '2\tquick\tner_1/1\tQUICK\tupper_1/0\n'
    )
    assert '3\tshe\tner_2/1\tSHE\tupper_2/0\n' in out


def test_print_conll_other_tags_repeated_other_tag_filtered(capsys):
    print_conll_style_tags_for_communication(
        comm_with_other_tags('upper', 'ner'),
        ner=True,
        other_tags=dict(
            upper=lambda anns: filter(lambda ann: ann.metadata.tool == 'tool/0', anns)
        ))
    (out, err) = capsys.readouterr()
    assert err == ''
    assert out.startswith(
        'INDEX\tTOKEN\tNER\tupper\n'
        '-----\t-----\t---\t-----\n'
        '1\tThe\tner_0/1\tupper_0/0\n'
        '2\tquick\tner_1/1\tupper_1/0\n'
    )
    assert '3\tshe\tner_2/1\tupper_2/0\n' in out


def test_print_conll_other_tags_repeated_ner(capsys):
    print_conll_style_tags_for_communication(
        comm_with_other_tags('ner', 'ner'),
        ner=True,
        other_tags=dict(upper=None))
    (out, err) = capsys.readouterr()
    assert err == ''
    assert out.startswith(
        'INDEX\tTOKEN\tNER\tNER\tupper\n'
        '-----\t-----\t---\t---\t-----\n'
        '1\tThe\tner_0/0\tner_0/1\tTHE\n'
        '2\tquick\tner_1/0\tner_1/1\tQUICK\n'
    )
    assert '3\tshe\tner_2/0\tner_2/1\tSHE\n' in out


def test_print_conll_other_tags_repeated_ner_filtered(capsys):
    print_conll_style_tags_for_communication(
        comm_with_other_tags('ner', 'ner'),
        ner=True,
        other_tags=dict(upper=None),
        ner_filter=lambda anns: filter(lambda ann: ann.metadata.tool == 'tool/1', anns))
    (out, err) = capsys.readouterr()
    assert err == ''
    assert out.startswith(
        'INDEX\tTOKEN\tNER\tupper\n'
        '-----\t-----\t---\t-----\n'
        '1\tThe\tner_0/1\tTHE\n'
        '2\tquick\tner_1/1\tQUICK\n'
    )
    assert '3\tshe\tner_2/1\tSHE\n' in out


def test_print_situation_mentions(capsys):
    comm = _comm_with_properties(0)
    print_situation_mentions(comm)
    (out, err) = capsys.readouterr()
    assert err == ''
    assert re.search(r'SituationMention\s+(\d+)-(\d+):\n', out)
    assert not re.search(r'situationType:', out)
    assert not re.search(r'situationKind:', out)
    assert not re.search(r'intensity:', out)


def test_print_situation_mentions_with_type(capsys):
    comm = _comm_with_properties(0)
    comm.situationMentionSetList[0].mentionList[0].situationType = u'st'
    print_situation_mentions(comm)
    (out, err) = capsys.readouterr()
    assert err == ''
    assert re.search(
        r'SituationMention +(\d+)-(\d+):\n +situationType: +st\n', out)
    assert not re.search(r'situationKind:', out)
    assert not re.search(r'intensity:', out)


def test_print_situation_mentions_with_kind(capsys):
    comm = _comm_with_properties(0)
    comm.situationMentionSetList[0].mentionList[0].situationKind = u'sk'
    print_situation_mentions(comm)
    (out, err) = capsys.readouterr()
    assert err == ''
    assert re.search(
        r'SituationMention +(\d+)-(\d+):\n +situationKind: +sk\n', out)
    assert not re.search(r'situationType:', out)
    assert not re.search(r'intensity:', out)


def test_print_situation_mentions_with_intensity(capsys):
    comm = _comm_with_properties(0)
    comm.situationMentionSetList[0].mentionList[0].intensity = 3.5
    print_situation_mentions(comm)
    (out, err) = capsys.readouterr()
    assert err == ''
    assert re.search(
        r'SituationMention +(\d+)-(\d+):\n +intensity: +3\.50*\n', out)
    assert not re.search(r'situationType:', out)
    assert not re.search(r'situationKind:', out)


def test_print_situation_mentions_without_properties(capsys):
    print_situation_mentions(_comm_with_properties(0))
    (out, err) = capsys.readouterr()
    assert 'Properties' not in out


@mark.parametrize('num_properties', [(1,), (2,), (3,)])
def test_print_situation_mentions_with_properties(capsys, num_properties):
    num_properties = 3
    print_situation_mentions(_comm_with_properties(num_properties))
    (out, err) = capsys.readouterr()
    assert 1 == out.count("Properties")
    assert 1 == out.count("Annotator1")
    assert num_properties == out.count("Property")
    assert num_properties == out.count("4.0")


def test_get_conll_tags_no_token_list():
    tokenization = Tokenization()

    assert _get_conll_tags_for_tokenization(tokenization) == []

    mock_filter = Mock(return_value=[])
    assert _get_conll_tags_for_tokenization(tokenization, mock_filter) == []


def test_get_conll_tags_zero_tokens_implicit_filter():
    tokenization = Tokenization(
        tokenList=TokenList(tokenList=[]),
        dependencyParseList=[
            DependencyParse(dependencyList=[]),
        ]
    )

    assert _get_conll_tags_for_tokenization(tokenization) == [[]]


def test_get_conll_tags_zero_tokens():
    tokenization = Tokenization(
        tokenList=TokenList(tokenList=[]),
        dependencyParseList=sentinel.dpl,
    )

    mock_filter = Mock(return_value=[
        DependencyParse(dependencyList=[]),
    ])
    assert _get_conll_tags_for_tokenization(tokenization, mock_filter) == [[]]
    mock_filter.assert_called_with(sentinel.dpl)


def test_get_conll_tags_one_token_implicit_filter():
    tokenization = Tokenization(
        tokenList=TokenList(tokenList=[
            Token(tokenIndex=0, text='t0'),
        ]),
        dependencyParseList=[
            DependencyParse(dependencyList=[
                Dependency(gov=-1, dep=0, edgeType='edge_0/0'),
            ]),
        ],
    )

    assert _get_conll_tags_for_tokenization(tokenization) == [
        [(u'0', u'edge_0/0')],
    ]


def test_get_conll_tags_one_token():
    tokenization = Tokenization(
        tokenList=TokenList(tokenList=[
            Token(tokenIndex=0, text='t0'),
        ]),
        dependencyParseList=sentinel.dpl,
    )

    mock_filter_zero = Mock(return_value=[])
    assert _get_conll_tags_for_tokenization(tokenization, mock_filter_zero) == []
    mock_filter_zero.assert_called_with(sentinel.dpl)

    mock_filter_one_empty = Mock(return_value=[
        DependencyParse(dependencyList=[]),
    ])
    assert _get_conll_tags_for_tokenization(tokenization, mock_filter_one_empty) == [
        [(u'', u'')],
    ]
    mock_filter_one_empty.assert_called_with(sentinel.dpl)

    mock_filter_one = Mock(return_value=[
        DependencyParse(dependencyList=[
            Dependency(gov=-1, dep=0, edgeType='edge_0/0'),
        ]),
    ])
    assert _get_conll_tags_for_tokenization(tokenization, mock_filter_one) == [
        [(u'0', u'edge_0/0')],
    ]
    mock_filter_one.assert_called_with(sentinel.dpl)

    mock_filter_two = Mock(return_value=[
        DependencyParse(dependencyList=[
            Dependency(gov=-1, dep=0, edgeType='edge_0/0'),
        ]),
        DependencyParse(dependencyList=[
            Dependency(gov=-1, dep=0, edgeType='edge_0/1'),
        ]),
    ])
    assert _get_conll_tags_for_tokenization(tokenization, mock_filter_two) == [
        [(u'0', u'edge_0/0')],
        [(u'0', u'edge_0/1')],
    ]
    mock_filter_two.assert_called_with(sentinel.dpl)


def test_get_conll_tags_two_tokens():
    tokenization = Tokenization(
        tokenList=TokenList(tokenList=[
            Token(tokenIndex=0, text='t0'),
            Token(tokenIndex=1, text='t1'),
        ]),
        dependencyParseList=sentinel.dpl,
    )

    mock_filter_zero = Mock(return_value=[])
    assert _get_conll_tags_for_tokenization(tokenization, mock_filter_zero) == []
    mock_filter_zero.assert_called_with(sentinel.dpl)

    mock_filter_one_empty = Mock(return_value=[
        DependencyParse(dependencyList=[]),
    ])
    assert _get_conll_tags_for_tokenization(tokenization, mock_filter_one_empty) == [
        [(u'', u''), (u'', u'')],
    ]
    mock_filter_one_empty.assert_called_with(sentinel.dpl)

    mock_filter_one_half_empty = Mock(return_value=[
        DependencyParse(dependencyList=[
            Dependency(gov=0, dep=1, edgeType='edge_1/0'),
        ]),
    ])
    assert _get_conll_tags_for_tokenization(tokenization, mock_filter_one_half_empty) == [
        [(u'', u''), (u'1', u'edge_1/0')],
    ]
    mock_filter_one_half_empty.assert_called_with(sentinel.dpl)

    mock_filter_one = Mock(return_value=[
        DependencyParse(dependencyList=[
            Dependency(gov=-1, dep=0, edgeType='edge_0/0'),
            Dependency(gov=0, dep=1, edgeType='edge_1/0'),
        ]),
    ])
    assert _get_conll_tags_for_tokenization(tokenization, mock_filter_one) == [
        [(u'0', u'edge_0/0'), (u'1', u'edge_1/0')],
    ]
    mock_filter_one.assert_called_with(sentinel.dpl)

    mock_filter_two = Mock(return_value=[
        DependencyParse(dependencyList=[
            Dependency(gov=-1, dep=0, edgeType='edge_0/0'),
            Dependency(gov=0, dep=1, edgeType='edge_1/0'),
        ]),
        DependencyParse(dependencyList=[
            Dependency(gov=-1, dep=0, edgeType='edge_0/1'),
            Dependency(gov=0, dep=1, edgeType='edge_1/1'),
        ]),
    ])
    assert _get_conll_tags_for_tokenization(tokenization, mock_filter_two) == [
        [(u'0', u'edge_0/0'), (u'1', u'edge_1/0')],
        [(u'0', u'edge_0/1'), (u'1', u'edge_1/1')],
    ]
    mock_filter_two.assert_called_with(sentinel.dpl)
