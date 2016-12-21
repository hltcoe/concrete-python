from concrete.inspect import (
    _reconcile_index_and_tool,
    _valid_index_lun,
    _get_conll_deprel_tags_for_tokenization as cdt
)

from concrete import (AnnotationMetadata,
                      Dependency,
                      DependencyParse,
                      Tokenization,
                      TokenizationKind,
                      Token,
                      TokenList,
                      UUID)

import time


class ReconcileIndexAndTool:

    default_tool = "My awesome tool"

    def __init__(self, num, t=default_tool):
        self.lst = [
            DependencyParse(
                uuid=UUID(uuidString=unicode(1)),
                metadata=AnnotationMetadata(
                    timestamp=int(time.time()),
                    tool=t if i == 0 else u"tool_" + unicode(i)
                ),
                dependencyList=[]
            ) for i in xrange(num)
        ] if num is not None else None


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
    assert _valid_index_lun(xrange(1), 0)
    assert not _valid_index_lun(xrange(1), -2)
    assert not _valid_index_lun(xrange(1), 1)


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
                                 text=unicode(i))
                           for i in xrange(num)]
            )
            self.tokenization.dependencyParseList = [
                DependencyParse(
                    uuid=UUID(uuidString=u"depparse_" + unicode(num)),
                    metadata=AnnotationMetadata(
                        timestamp=int(time.time()),
                        tool=t if dp_idx == 0 else
                        (u"dptool" + unicode(dp_idx))
                    ),
                    dependencyList=[
                        Dependency(
                            gov=i-1, dep=i,
                            edgeType=u"edge_" + unicode(i) +
                            "/" + unicode(dp_idx)
                        ) for i in xrange(num)
                    ]
                ) for dp_idx in xrange(num_dp)
            ]


def test_get_conll_deprel_tags_none_tokens():
    tokenization = FakeTokenizationAndDependency(None).tokenization
    for i in xrange(-1, 2):
        for tool in (None, "", FakeTokenizationAndDependency.default_tool):
            assert cdt(tokenization, i, tool) == []


def test_get_conll_deprel_tags_zero_tokens():
    tokenization = FakeTokenizationAndDependency(0).tokenization
    for i in xrange(-1, 2):
        for tool in (None, "", FakeTokenizationAndDependency.default_tool):
            assert cdt(tokenization, i, tool) == []


def test_get_conll_deprel_tags_one_tokens_found():
    tokenization = FakeTokenizationAndDependency(1).tokenization
    assert cdt(tokenization, 0, None) == [u"edge_0/0"]
    assert (
        cdt(tokenization, 0, FakeTokenizationAndDependency.default_tool) ==
        [u"edge_0/0"])
    assert cdt(tokenization, 0, "") == [""]

    for tool in (None, ""):
        assert cdt(tokenization, -1, tool) == [""]

    assert (
        cdt(tokenization, -1, FakeTokenizationAndDependency.default_tool) ==
        [u"edge_0/0"])

    assert (
        cdt(tokenization, 1, FakeTokenizationAndDependency.default_tool) ==
        [u"edge_0/0"])
    for tool in (None, ""):
        assert cdt(tokenization, 1, tool) == [""]


def test_get_conll_deprel_tags_arbitrary_num_tokens_not_found():
    t = "Other great tool"
    for num_tokens in xrange(1, 10):
        tokenization = FakeTokenizationAndDependency(num_tokens,
                                                     t=t).tokenization
        assert cdt(tokenization, 0, None) == [u"edge_" + unicode(i) + "/0"
                                              for i in xrange(num_tokens)]
        assert (
            cdt(tokenization, 0, FakeTokenizationAndDependency.default_tool)
            == [""] * num_tokens)
        assert cdt(tokenization, 0, "") == [""] * num_tokens

        assert cdt(tokenization, -1, None) == [""] * num_tokens
        assert tokenization.tokenList

        assert cdt(tokenization, 0, None) == [u"edge_" + unicode(j) + "/0"
                                              for j in xrange(num_tokens)]
        for tool in ("", FakeTokenizationAndDependency.default_tool):
            assert cdt(tokenization, 0, tool) == [""] * num_tokens

        for i in xrange(1, num_tokens+1):
            for tool in (None, "",
                         FakeTokenizationAndDependency.default_tool):
                assert cdt(tokenization, i, tool) == [""] * num_tokens


def test_get_conll_deprel_tags_arbitrary_num_tokens_num_dp_not_found():
    t = "Other great tool"
    # without this memoization, style fails
    style_tool = FakeTokenizationAndDependency.default_tool
    for num_dp in xrange(1, 4):
        for num_tokens in xrange(1, 10):
            tokenization = FakeTokenizationAndDependency(num_tokens,
                                                         num_dp=num_dp,
                                                         t=t).tokenization

            # no tool given, with valid index: return indexed parse
            assert cdt(tokenization, 0, None) == [u"edge_" + unicode(i) + "/0"
                                                  for i in xrange(num_tokens)]
            # tools given, with valid index, but not found
            assert cdt(tokenization, 0, style_tool) == [""] * num_tokens
            assert cdt(tokenization, 0, "") == [""] * num_tokens

            # invalid index, no tool given: return empty
            assert cdt(tokenization, -1, None) == [""] * num_tokens

            for i in xrange(num_dp):
                # no tool given, valid index: return specified parse
                assert cdt(tokenization, i, None) == [
                    u"edge_" + unicode(j) + "/" + unicode(i)
                    for j in xrange(num_tokens)]
                # tool given, valid index, not found: return empty
                for tool in ("",
                             FakeTokenizationAndDependency.default_tool):
                    assert cdt(tokenization, i, tool) == [""] * num_tokens

            # invalid index: return empty
            for tool in (None, "",
                         FakeTokenizationAndDependency.default_tool):
                assert cdt(tokenization, num_dp, tool) == [""] * num_tokens


def test_get_conll_deprel_tags_arbitrary_num_tokens_num_dp_found():
    # sigh... memoize to let style checks pass
    style_tool = FakeTokenizationAndDependency.default_tool
    for num_dp in xrange(1, 4):
        for num_tokens in xrange(1, 10):
            tokenization = FakeTokenizationAndDependency(
                num_tokens,
                num_dp=num_dp).tokenization

            # no tool given, with valid index: return indexed parse
            assert cdt(tokenization, 0, None) == [u"edge_" + unicode(i) + "/0"
                                                  for i in xrange(num_tokens)]
            # tool given, with valid index, not found
            assert cdt(tokenization, 0, style_tool) == [
                u"edge_" + unicode(i) + "/0" for i in xrange(num_tokens)]
            assert cdt(tokenization, 0, "") == [""] * num_tokens

            # invalid index, no tool given: return empty
            assert cdt(tokenization, -1, None) == [""] * num_tokens

            for i in xrange(num_dp):
                # tool given, valid index, not found: return empty
                assert cdt(tokenization, i, "") == [""] * num_tokens
                # tool none, valid index, found: return requested
                assert cdt(tokenization, i, None) == [
                    u"edge_" + unicode(j) + "/" + unicode(i)
                    for j in xrange(num_tokens)]
                # tool given, valid index, found: return correct
                assert cdt(tokenization, i, style_tool) == [
                    u"edge_" + unicode(j) + "/0" for j in xrange(num_tokens)]

            # invalid index: return empty
            for tool in (None, ""):
                assert cdt(tokenization, num_dp, tool) == [""] * num_tokens

            assert cdt(tokenization, num_dp, style_tool) == [
                u"edge_" + unicode(j) + "/0" for j in xrange(num_tokens)]
