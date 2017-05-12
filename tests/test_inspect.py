from __future__ import unicode_literals
from __future__ import print_function
import time

from pytest import mark, fixture

from concrete.inspect import (
    _reconcile_index_and_tool,
    _valid_index_lun,
    _get_conll_deprel_tags_for_tokenization as cdt,
    print_situation_mentions,
    print_conll_style_tags_for_communication,
)
from concrete.util import generate_UUID as genId, create_comm
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
    UUID,
)


def _comm_with_properties(num_properties):
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
            value="Property%d" % i,
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


@fixture
def comm_with_other_tags():
    comm = create_comm('quick', '''\
The quick brown fox jumped
over the lazy dog .

Or did she ?
''')
    for section in comm.sectionList:
        for sentence in section.sentenceList:
            sentence.tokenization.tokenTaggingList = [
                TokenTagging(
                    uuid=genId(),
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
                    uuid=genId(),
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
            ]
    return comm


def test_print_conll_other_tags_ignore_all(capsys, comm_with_other_tags):
    print_conll_style_tags_for_communication(comm_with_other_tags)
    (out, err) = capsys.readouterr()
    assert err == ''
    assert out.startswith(
        'INDEX\tTOKEN\n'
        '-----\t-----\n'
        '1\tThe\n'
        '2\tquick\n'
    )


def test_print_conll_other_tags_ignore_some(capsys, comm_with_other_tags):
    print_conll_style_tags_for_communication(comm_with_other_tags,
                                             other_tags=('upper',))
    (out, err) = capsys.readouterr()
    assert err == ''
    assert out.startswith(
        'INDEX\tTOKEN\tupper\n'
        '-----\t-----\t-----\n'
        '1\tThe\tTHE\n'
        '2\tquick\tQUICK\n'
    )
    assert '3\tshe\tSHE\n' in out


def test_print_conll_other_tags(capsys, comm_with_other_tags):
    print_conll_style_tags_for_communication(comm_with_other_tags,
                                             other_tags=('upper', 'lower'))
    (out, err) = capsys.readouterr()
    assert err == ''
    assert out.startswith(
        'INDEX\tTOKEN\tupper\tlower\n'
        '-----\t-----\t-----\t-----\n'
        '1\tThe\tTHE\tthe\n'
        '2\tquick\tQUICK\tquick\n'
    )
    assert '3\tshe\tSHE\tshe\n' in out


class ReconcileIndexAndTool:

    default_tool = "My awesome tool"

    def __init__(self, num, t=default_tool):
        self.lst = [
            DependencyParse(
                uuid=UUID(uuidString=str(1)),
                metadata=AnnotationMetadata(
                    timestamp=int(time.time()),
                    tool=t if i == 0 else "tool_" + str(i)
                ),
                dependencyList=[]
            ) for i in range(num)
        ] if num is not None else None


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


def test_reconcile_index_and_tool_none_list():
    lst = ReconcileIndexAndTool(None).lst
    assert _reconcile_index_and_tool(lst, 0, None) == -1
    assert _reconcile_index_and_tool(lst, -2, None) == -1
    assert _reconcile_index_and_tool(lst, 0, "My awesome tool") == -1


def test_reconcile_index_and_tool_empty_list():
    lst = ReconcileIndexAndTool(0).lst
    assert _reconcile_index_and_tool(lst, 0, None) == -1
    assert _reconcile_index_and_tool(lst, -2, None) == -1
    assert _reconcile_index_and_tool(lst, 0, "My awesome tool") == -1


def test_reconcile_index_and_tool_singleton_list():
    lst = ReconcileIndexAndTool(1).lst
    assert _reconcile_index_and_tool(lst, 0, None) == 0
    assert _reconcile_index_and_tool(lst, -2, None) == -2
    assert _reconcile_index_and_tool(lst, 0, "My awesome tool") == 0
    assert _reconcile_index_and_tool(lst, 0, "Your awesome tool") == -1


def test_reconcile_index_and_tool_three_list():
    lst = ReconcileIndexAndTool(3).lst
    assert _reconcile_index_and_tool(lst, 0, None) == 0
    assert _reconcile_index_and_tool(lst, -2, None) == -2
    assert _reconcile_index_and_tool(lst, 0, "My awesome tool") == 0
    assert _reconcile_index_and_tool(lst, 0, "Your awesome tool") == -1
    tmp = lst[0]
    lst[0] = lst[2]
    lst[2] = tmp
    assert _reconcile_index_and_tool(lst, 0, "My awesome tool") == 2
    assert _reconcile_index_and_tool(lst, 3, "My awesome tool") == 2
    assert _reconcile_index_and_tool(lst, 3, "Your awesome tool") == -1


def test_valid_index_lun_none_list():
    assert not _valid_index_lun(None, 0)
    assert not _valid_index_lun(None, -2)
    assert not _valid_index_lun(None, 0)


def test_valid_index_lun_empty_list():
    assert not _valid_index_lun([], 0)
    assert not _valid_index_lun([], -2)
    assert not _valid_index_lun([], 0)


def test_valid_index_lun_singleton_list():
    assert _valid_index_lun(range(1), 0)
    assert not _valid_index_lun(range(1), -2)
    assert not _valid_index_lun(range(1), 1)


class FakeTokenizationAndDependency:

    default_tool = "My awesome tool"

    def __init__(self, num, num_dp=1, t=default_tool):
        self.tokenization = Tokenization(
            uuid=UUID(uuidString=u"id"),
            metadata=AnnotationMetadata(
                timestamp=int(time.time()),
                tool=u"tool"
            ),
            kind=TokenizationKind.TOKEN_LIST,
        )
        if num is not None:
            self.tokenization.tokenList = TokenList(
                tokenList=[Token(tokenIndex=i,
                                 text=str(i))
                           for i in range(num)]
            )
            self.tokenization.dependencyParseList = [
                DependencyParse(
                    uuid=UUID(uuidString=u"depparse_" + str(num)),
                    metadata=AnnotationMetadata(
                        timestamp=int(time.time()),
                        tool=t if dp_idx == 0 else
                        ("dptool" + str(dp_idx))
                    ),
                    dependencyList=[
                        Dependency(
                            gov=i-1, dep=i,
                            edgeType="edge_" + str(i) +
                            "/" + str(dp_idx)
                        ) for i in range(num)
                    ]
                ) for dp_idx in range(num_dp)
            ]


def test_get_conll_deprel_tags_none_tokens():
    tokenization = FakeTokenizationAndDependency(None).tokenization
    for i in range(-1, 2):
        for tool in (None, "", FakeTokenizationAndDependency.default_tool):
            assert list(cdt(tokenization, i, tool)) == []


def test_get_conll_deprel_tags_zero_tokens():
    tokenization = FakeTokenizationAndDependency(0).tokenization
    for i in range(-1, 2):
        for tool in (None, "", FakeTokenizationAndDependency.default_tool):
            assert list(cdt(tokenization, i, tool)) == []


def test_get_conll_deprel_tags_one_tokens_found():
    tokenization = FakeTokenizationAndDependency(1).tokenization
    assert list(cdt(tokenization, 0, None)) == [u"edge_0/0"]
    assert (
        list(cdt(tokenization, 0, FakeTokenizationAndDependency.default_tool)) ==
        [u"edge_0/0"])
    assert list(cdt(tokenization, 0, "")) == [""]

    for tool in (None, ""):
        assert list(cdt(tokenization, -1, tool)) == [""]

    assert (
        list(cdt(tokenization, -1, FakeTokenizationAndDependency.default_tool)) ==
        [u"edge_0/0"])

    assert (
        list(cdt(tokenization, 1, FakeTokenizationAndDependency.default_tool)) ==
        [u"edge_0/0"])
    for tool in (None, ""):
        assert list(cdt(tokenization, 1, tool)) == [""]


def test_get_conll_deprel_tags_arbitrary_num_tokens_not_found():
    t = "Other great tool"
    for num_tokens in range(1, 10):
        tokenization = FakeTokenizationAndDependency(num_tokens,
                                                     t=t).tokenization
        assert list(cdt(tokenization, 0, None)) == ["edge_" + str(i) + "/0"
                                                    for i in range(num_tokens)]
        assert (
            list(cdt(tokenization, 0, FakeTokenizationAndDependency.default_tool)) ==
            [""] * num_tokens
        )
        assert list(cdt(tokenization, 0, "")) == [""] * num_tokens

        assert list(cdt(tokenization, -1, None)) == [""] * num_tokens
        assert tokenization.tokenList

        assert list(cdt(tokenization, 0, None)) == ["edge_" + str(j) + "/0"
                                                    for j in range(num_tokens)]
        for tool in ("", FakeTokenizationAndDependency.default_tool):
            assert list(cdt(tokenization, 0, tool)) == [""] * num_tokens

        for i in range(1, num_tokens+1):
            for tool in (None, "",
                         FakeTokenizationAndDependency.default_tool):
                assert list(cdt(tokenization, i, tool)) == [""] * num_tokens


def test_get_conll_deprel_tags_arbitrary_num_tokens_num_dp_not_found():
    t = "Other great tool"
    # without this memoization, style fails
    style_tool = FakeTokenizationAndDependency.default_tool
    for num_dp in range(1, 4):
        for num_tokens in range(1, 10):
            tokenization = FakeTokenizationAndDependency(num_tokens,
                                                         num_dp=num_dp,
                                                         t=t).tokenization

            # no tool given, with valid index: return indexed parse
            assert list(cdt(tokenization, 0, None)) == ["edge_" + str(i) + "/0"
                                                        for i in range(num_tokens)]
            # tools given, with valid index, but not found
            assert list(cdt(tokenization, 0, style_tool)) == [""] * num_tokens
            assert list(cdt(tokenization, 0, "")) == [""] * num_tokens

            # invalid index, no tool given: return empty
            assert list(cdt(tokenization, -1, None)) == [""] * num_tokens

            for i in range(num_dp):
                # no tool given, valid index: return specified parse
                assert list(cdt(tokenization, i, None)) == [
                    "edge_" + str(j) + "/" + str(i)
                    for j in range(num_tokens)]
                # tool given, valid index, not found: return empty
                for tool in ("",
                             FakeTokenizationAndDependency.default_tool):
                    assert list(cdt(tokenization, i, tool)) == [""] * num_tokens

            # invalid index: return empty
            for tool in (None, "",
                         FakeTokenizationAndDependency.default_tool):
                assert list(cdt(tokenization, num_dp, tool)) == [""] * num_tokens


def test_get_conll_deprel_tags_arbitrary_num_tokens_num_dp_found():
    # sigh... memoize to let style checks pass
    style_tool = FakeTokenizationAndDependency.default_tool
    for num_dp in range(1, 4):
        for num_tokens in range(1, 10):
            tokenization = FakeTokenizationAndDependency(
                num_tokens,
                num_dp=num_dp).tokenization

            # no tool given, with valid index: return indexed parse
            assert list(cdt(tokenization, 0, None)) == ["edge_" + str(i) + "/0"
                                                        for i in range(num_tokens)]
            # tool given, with valid index, not found
            assert list(cdt(tokenization, 0, style_tool)) == [
                "edge_" + str(i) + "/0" for i in range(num_tokens)]
            assert list(cdt(tokenization, 0, "")) == [""] * num_tokens

            # invalid index, no tool given: return empty
            assert list(cdt(tokenization, -1, None)) == [""] * num_tokens

            for i in range(num_dp):
                # tool given, valid index, not found: return empty
                assert list(cdt(tokenization, i, "")) == [""] * num_tokens
                # tool none, valid index, found: return requested
                assert list(cdt(tokenization, i, None)) == [
                    "edge_" + str(j) + "/" + str(i)
                    for j in range(num_tokens)]
                # tool given, valid index, found: return correct
                assert list(cdt(tokenization, i, style_tool)) == [
                    "edge_" + str(j) + "/0" for j in range(num_tokens)]

            # invalid index: return empty
            for tool in (None, ""):
                assert list(cdt(tokenization, num_dp, tool)) == [""] * num_tokens

            assert list(cdt(tokenization, num_dp, style_tool)) == [
                "edge_" + str(j) + "/0" for j in range(num_tokens)]
