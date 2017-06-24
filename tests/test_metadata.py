from __future__ import unicode_literals
from datetime import datetime
import random
import string

from pytest import raises
from mock import Mock, sentinel, patch

from concrete.util import (
    get_index_of_tool, datetime_to_timestamp, now_timestamp,
    timestamp_to_datetime, get_annotation_field, filter_annotations
)
from concrete import AnnotationMetadata


class HasMetadata(object):
    def __init__(self, tool=None):
        self.metadata = AnnotationMetadata(
            tool=HasMetadata.gen_tool(tool),
            timestamp=0,
        )

    @classmethod
    def gen_tool(cls, tool=None, size=6,
                 chars=string.ascii_uppercase + string.digits):
        return tool if (tool is not None) else \
            u''.join(random.choice(chars) for _ in range(size))


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


def test_timestamp_to_datetime():
    assert timestamp_to_datetime(0) == datetime(1970, 1, 1)
    assert timestamp_to_datetime(47) == datetime(1970, 1, 1, 0, 0, 47)


def test_now_timestamp():
    assert now_timestamp() > datetime_to_timestamp(datetime(2000, 1, 1, 0, 0, 0))


def test_get_annotation_field_kBest():
    annotation = Mock(metadata=Mock(kBest=4))
    assert get_annotation_field(annotation, 'kBest') == 4


def test_get_annotation_field_tool():
    annotation = Mock(metadata=Mock(tool='goldenhorse'))
    assert get_annotation_field(annotation, 'tool') == 'goldenhorse'


def test_get_annotation_field_timestamp():
    annotation = Mock(metadata=Mock(timestamp=4))
    assert get_annotation_field(annotation, 'timestamp') == 4


def test_get_annotation_field_invalid():
    annotation = Mock(metadata=Mock())
    with raises(ValueError):
        get_annotation_field(annotation, 'foobar')


def test_filter_annotations_noop():
    assert filter_annotations([
        sentinel.annotation0,
        sentinel.annotation1,
        sentinel.annotation2,
    ]) == [
        sentinel.annotation0,
        sentinel.annotation1,
        sentinel.annotation2,
    ]


@patch('concrete.util.metadata.get_annotation_field')
def test_filter_annotations(mock_get_annotation_field):
    def _mock_get_annotation_field(annotation, field):
        if field == 'foo':
            return 3 if (
                annotation in (sentinel.annotation0, sentinel.annotation1)
            ) else 4
        elif field == 'bar':
            return 4 if (
                annotation in (sentinel.annotation1, sentinel.annotation2)
            ) else 3
        else:
            raise ValueError('bad field')
    mock_get_annotation_field.side_effect = _mock_get_annotation_field

    assert filter_annotations(
        [
            sentinel.annotation0,
            sentinel.annotation1,
            sentinel.annotation2,
        ],
        filter_field_value_pairs=(('foo', 3), ('bar', 4))
    ) == [sentinel.annotation1]

# def filter_annotations(annotations,
#                        filter_field_value_pairs=None,
#                        sort_field=None,
#                        sort_reverse=False,
#                        action_if_multiple='pass',
#                        action_if_zero='pass'):
