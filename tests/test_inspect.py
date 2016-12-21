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
import unittest


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

class TestReconcileIndexAndTool(unittest.TestCase):

    def test_none_list(self):
        lst = ReconcileIndexAndTool(None).lst
        self.assertEqual(_reconcile_index_and_tool(lst, 0, None), -1)
        self.assertEqual(_reconcile_index_and_tool(lst, -2, None), -1)
        self.assertEqual(_reconcile_index_and_tool(lst,
                                                   0,
                                                   "My awesome tool"),
                         -1)

    def test_empty_list(self):
        lst = ReconcileIndexAndTool(0).lst
        self.assertEqual(_reconcile_index_and_tool(lst, 0, None), -1)
        self.assertEqual(_reconcile_index_and_tool(lst, -2, None), -1)
        self.assertEqual(_reconcile_index_and_tool(lst,
                                                   0,
                                                   "My awesome tool"),
                         -1)
        
    def test_singleton_list(self):
        lst = ReconcileIndexAndTool(1).lst
        self.assertEqual(_reconcile_index_and_tool(lst, 0, None), 0)
        self.assertEqual(_reconcile_index_and_tool(lst, -2, None), -2)
        self.assertEqual(_reconcile_index_and_tool(lst,
                                                   0,
                                                   "My awesome tool"),
                         0)
        self.assertEqual(_reconcile_index_and_tool(lst,
                                                   0,
                                                   "Your awesome tool"),
                         -1)

    def test_three_list(self):
        lst = ReconcileIndexAndTool(3).lst
        self.assertEqual(_reconcile_index_and_tool(lst, 0, None), 0)
        self.assertEqual(_reconcile_index_and_tool(lst, -2, None), -2)
        self.assertEqual(_reconcile_index_and_tool(lst,
                                                   0,
                                                   "My awesome tool"),
                         0)
        self.assertEqual(_reconcile_index_and_tool(lst,
                                                   0,
                                                   "Your awesome tool"),
                         -1)
        tmp = lst[0]
        lst[0] = lst[2]
        lst[2] = tmp
        self.assertEqual(_reconcile_index_and_tool(lst,
                                                   0,
                                                   "My awesome tool"),
                         2)
        self.assertEqual(_reconcile_index_and_tool(lst,
                                                   3,
                                                   "My awesome tool"),
                         2)
        self.assertEqual(_reconcile_index_and_tool(lst,
                                                   3,
                                                   "Your awesome tool"),
                         -1)

class TestValidIndexLUn(unittest.TestCase):

    def test_none_list(self):
        self.assertFalse(_valid_index_lun(None, 0))
        self.assertFalse(_valid_index_lun(None, -2))
        self.assertFalse(_valid_index_lun(None, 0))

    def test_empty_list(self):
        self.assertFalse(_valid_index_lun([], 0))
        self.assertFalse(_valid_index_lun([], -2))
        self.assertFalse(_valid_index_lun([], 0))
        
    def test_singleton_list(self):
        self.assertTrue(_valid_index_lun(xrange(1), 0))
        self.assertFalse(_valid_index_lun(xrange(1), -2))
        self.assertFalse(_valid_index_lun(xrange(1), 1))

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
            self.tokenization.tokenList=TokenList(
                tokenList=[Token(tokenIndex=i,
                                 text=unicode(i))
                           for i in xrange(num)]
            )
            self.tokenization.dependencyParseList=[
                DependencyParse(
                    uuid=UUID(uuidString=u"depparse_" + unicode(num)),
                    metadata=AnnotationMetadata(
                        timestamp=int(time.time()),
                        tool=t if dp_idx == 0 else (u"dptool" + unicode(dp_idx))
                    ),
                    dependencyList=[
                        Dependency(
                            gov=i-1, dep=i,
                            edgeType=u"edge_" + unicode(i) + "/" + unicode(dp_idx)
                        ) for i in xrange(num)
                    ]
                ) for dp_idx in xrange(num_dp)
            ]
        
class TestGetCoNLLDeprelTags(unittest.TestCase):

    def test_none_tokens(self):
        tokenization=FakeTokenizationAndDependency(None).tokenization
        for i in xrange(-1, 2):
            for tool in (None, "", FakeTokenizationAndDependency.default_tool):
                self.assertEqual(cdt(tokenization, i, tool), [])

    def test_zero_tokens(self):
        tokenization=FakeTokenizationAndDependency(0).tokenization
        for i in xrange(-1, 2):
            for tool in (None, "", FakeTokenizationAndDependency.default_tool):
                self.assertEqual(cdt(tokenization, i, tool), [])

    def test_one_tokens_found(self):
        tokenization=FakeTokenizationAndDependency(1).tokenization
        self.assertEqual(cdt(tokenization, 0, None),
                         [u"edge_0/0"])
        self.assertEqual(cdt(tokenization, 0, FakeTokenizationAndDependency.default_tool),
                         [u"edge_0/0"])
        self.assertEqual(cdt(tokenization, 0, ""), [""])

        for tool in (None, ""):
            self.assertEqual(cdt(tokenization, -1, tool), [""])

        self.assertEqual(cdt(tokenization, -1, FakeTokenizationAndDependency.default_tool),
                         [u"edge_0/0"])
        
        self.assertEqual(cdt(tokenization, 1,  FakeTokenizationAndDependency.default_tool),
                         [u"edge_0/0"])
        for tool in (None, ""):
            self.assertEqual(cdt(tokenization, 1, tool), [""])

    def test_arbitrary_num_tokens_not_found(self):
        for num_tokens in xrange(1, 10):
            tokenization=FakeTokenizationAndDependency(num_tokens, \
                                                       t="Other great tool").tokenization
            self.assertEqual(cdt(tokenization, 0, None),
                             [u"edge_" + unicode(i) + "/0" for i in xrange(num_tokens)])
            self.assertEqual(cdt(tokenization, 0, FakeTokenizationAndDependency.default_tool),
                             [""]*num_tokens)
            self.assertEqual(cdt(tokenization, 0, ""), [""]*num_tokens)

            self.assertEqual(cdt(tokenization, -1, None), \
                             [""] * num_tokens)
            self.assertTrue(tokenization.tokenList)

            self.assertEqual(cdt(tokenization, 0, None), \
                             [u"edge_" + unicode(j) + "/0" for j in xrange(num_tokens)])
            for tool in ("", FakeTokenizationAndDependency.default_tool):
                self.assertEqual(cdt(tokenization, 0, tool), [""] * num_tokens)
            
            for i in xrange(1, num_tokens+1):
                for tool in (None, "", FakeTokenizationAndDependency.default_tool):
                    self.assertEqual(cdt(tokenization, i, tool), [""] * num_tokens)

    def test_arbitrary_num_tokens_num_dp_not_found(self):
        for num_dp in xrange(1, 4):
            for num_tokens in xrange(1, 10):
                tokenization=FakeTokenizationAndDependency(num_tokens, \
                                                           num_dp=num_dp,
                                                           t="Other great tool").tokenization

                # no tool given, with valid index: return indexed parse
                self.assertEqual(cdt(tokenization, 0, None),
                                 [u"edge_" + unicode(i) + "/0" for i in xrange(num_tokens)])
                # tools given, with valid index, but not found
                self.assertEqual(cdt(tokenization, 0,
                                     FakeTokenizationAndDependency.default_tool),
                                 [""] * num_tokens)
                self.assertEqual(cdt(tokenization, 0, ""), [""] * num_tokens)

                # invalid index, no tool given: return empty
                self.assertEqual(cdt(tokenization, -1, None), \
                                 [""] * num_tokens)

                for i in xrange(num_dp):
                    # no tool given, valid index: return specified parse
                    self.assertEqual(cdt(tokenization, i, None), \
                                     [u"edge_" + unicode(j) + "/" + unicode(i)
                                      for j in xrange(num_tokens)])
                    # tool given, valid index, not found: return empty
                    for tool in ("", FakeTokenizationAndDependency.default_tool):
                        self.assertEqual(cdt(tokenization, i, tool), [""] * num_tokens)

                # invalid index: return empty
                for tool in (None, "", FakeTokenizationAndDependency.default_tool):
                    self.assertEqual(cdt(tokenization, num_dp, tool), [""] * num_tokens)

    def test_arbitrary_num_tokens_num_dp_found(self):
        for num_dp in xrange(1, 4):
            for num_tokens in xrange(1, 10):
                tokenization=FakeTokenizationAndDependency(num_tokens,
                                                           num_dp=num_dp).tokenization

                # no tool given, with valid index: return indexed parse
                self.assertEqual(cdt(tokenization, 0, None),
                                 [u"edge_" + unicode(i) + "/0" for i in xrange(num_tokens)])
                # tool given, with valid index, not found
                self.assertEqual(cdt(tokenization, 0,
                                     FakeTokenizationAndDependency.default_tool),
                                 [u"edge_" + unicode(i) + "/0" for i in xrange(num_tokens)])
                self.assertEqual(cdt(tokenization, 0, ""), [""] * num_tokens)

                # invalid index, no tool given: return empty
                self.assertEqual(cdt(tokenization, -1, None), \
                                 [""] * num_tokens)

                for i in xrange(num_dp):
                    # tool given, valid index, not found: return empty
                    self.assertEqual(cdt(tokenization, i, ""),
                                     [""] * num_tokens)
                    # tool none, valid index, found: return requested
                    self.assertEqual(cdt(tokenization, i, None),
                                     [u"edge_" + unicode(j) + "/" + unicode(i)
                                      for j in xrange(num_tokens)])
                    # tool given, valid index, found: return correct
                    self.assertEqual(cdt(tokenization, i,
                                     FakeTokenizationAndDependency.default_tool),
                                     [u"edge_" + unicode(j) + "/0"
                                      for j in xrange(num_tokens)])

                # invalid index: return empty
                for tool in (None, ""):
                    self.assertEqual(cdt(tokenization, num_dp, tool), [""] * num_tokens)

                self.assertEqual(cdt(tokenization, num_dp,
                                     FakeTokenizationAndDependency.default_tool),
                                 [u"edge_" + unicode(j) + "/0"
                                  for j in xrange(num_tokens)])
