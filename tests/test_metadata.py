from concrete.util.metadata import (
    get_index_of_tool
)

from concrete import AnnotationMetadata

import random
import string
import time
import unittest


class HasMetadata:

    def __init__(self, tool=None):
        self.metadata = AnnotationMetadata(
            tool=HasMetadata.gen_tool(tool),
            timestamp=int(time.time())
        )

    @classmethod
    def gen_tool(cls, tool=None, size=6,
                 chars=string.ascii_uppercase + string.digits):
        return tool if (tool is not None) else \
            u''.join(random.choice(chars) for _ in xrange(size))


class TestFindToolInList(unittest.TestCase):

    def test_none_list(self):
        self.assertEqual(get_index_of_tool(None, None), -1)
        self.assertEqual(get_index_of_tool(None, ""), -1)
        self.assertEqual(get_index_of_tool(None, "My awesome tool"), -1)

    def test_empty_list(self):
        self.assertEqual(get_index_of_tool([], None), -1)
        self.assertEqual(get_index_of_tool([], ""), -1)
        self.assertEqual(get_index_of_tool([], "My awesome tool"), -1)

    def test_nonempty_list_contains(self):
        lst = [
            HasMetadata("My awesome tool"),
            HasMetadata("My awesome tool--new"),
            HasMetadata()
        ]
        self.assertEqual(get_index_of_tool(lst, None), 0)
        self.assertEqual(get_index_of_tool(lst, ""), -1)
        self.assertEqual(get_index_of_tool(lst, "My awesome tool"), 0)
        lst[2] = lst[0]
        lst[0] = HasMetadata()
        self.assertEqual(get_index_of_tool(lst, None), 0)
        self.assertEqual(get_index_of_tool(lst, ""), -1)
        self.assertEqual(get_index_of_tool(lst, "My awesome tool"), 2)

    def test_nonempty_list_no_contains(self):
        lst = [
            HasMetadata(),
            HasMetadata(),
            HasMetadata()
        ]
        self.assertEqual(get_index_of_tool(lst, None), 0)
        self.assertEqual(get_index_of_tool(lst, ""), -1)
        self.assertEqual(get_index_of_tool(lst, "My awesome tool"), -1)
