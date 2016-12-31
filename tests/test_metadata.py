from concrete.util.metadata import (
    get_index_of_tool, datetime_to_timestamp
)

from concrete import AnnotationMetadata

from datetime import datetime
import random
import string


class HasMetadata:

    def __init__(self, tool=None):
        self.metadata = AnnotationMetadata(
            tool=HasMetadata.gen_tool(tool),
            timestamp=0,
        )

    @classmethod
    def gen_tool(cls, tool=None, size=6,
                 chars=string.ascii_uppercase + string.digits):
        return tool if (tool is not None) else \
            u''.join(random.choice(chars) for _ in xrange(size))


def test_get_index_of_tool_none_list():
    assert get_index_of_tool(None, None) == -1
    assert get_index_of_tool(None, "") == -1
    assert get_index_of_tool(None, "My awesome tool") == -1


def test_get_index_of_tool_empty_list():
    assert get_index_of_tool([], None) == -1
    assert get_index_of_tool([], "") == -1
    assert get_index_of_tool([], "My awesome tool") == -1


def test_get_index_of_tool_nonempty_list_contains():
    lst = [
        HasMetadata("My awesome tool"),
        HasMetadata("My awesome tool--new"),
        HasMetadata()
    ]
    assert get_index_of_tool(lst, None) == 0
    assert get_index_of_tool(lst, "") == -1
    assert get_index_of_tool(lst, "My awesome tool") == 0
    lst[2] = lst[0]
    lst[0] = HasMetadata()
    assert get_index_of_tool(lst, None) == 0
    assert get_index_of_tool(lst, "") == -1
    assert get_index_of_tool(lst, "My awesome tool") == 2


def test_get_index_of_tool_nonempty_list_no_contains():
    lst = [
        HasMetadata(),
        HasMetadata(),
        HasMetadata()
    ]
    assert get_index_of_tool(lst, None) == 0
    assert get_index_of_tool(lst, "") == -1
    assert get_index_of_tool(lst, "My awesome tool") == -1


def test_datetime_to_timestamp():
    assert datetime_to_timestamp(datetime(1970, 1, 1)) == 0
    assert datetime_to_timestamp(datetime(1970, 1, 1, 0, 0, 47)) == 47
