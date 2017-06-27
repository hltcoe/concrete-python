from __future__ import unicode_literals
from datetime import datetime
import random
import string

from pytest import raises
from mock import Mock, sentinel, patch

from concrete.util import (
    get_index_of_tool, datetime_to_timestamp, now_timestamp,
    timestamp_to_datetime, get_annotation_field, filter_annotations,
    ZeroAnnotationsError, MultipleAnnotationsError, filter_annotations_json,
    tool_to_filter
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
        return {
            (sentinel.annotation0, 'foo'): 3,
            (sentinel.annotation1, 'foo'): 3,
            (sentinel.annotation2, 'foo'): 4,
            (sentinel.annotation0, 'bar'): 3,
            (sentinel.annotation1, 'bar'): 4,
            (sentinel.annotation2, 'bar'): 4,
        }[(annotation, field)]
    mock_get_annotation_field.side_effect = _mock_get_annotation_field

    assert filter_annotations(
        [
            sentinel.annotation0,
            sentinel.annotation1,
            sentinel.annotation2,
        ],
        filter_fields={'foo': 3, 'bar': 4}
    ) == [sentinel.annotation1]


@patch('concrete.util.metadata.get_annotation_field')
def test_filter_annotations_zero(mock_get_annotation_field):
    def _mock_get_annotation_field(annotation, field):
        return {
            (sentinel.annotation0, 'foo'): 3,
            (sentinel.annotation1, 'foo'): 3,
            (sentinel.annotation2, 'foo'): 4,
            (sentinel.annotation0, 'bar'): 3,
            (sentinel.annotation1, 'bar'): 3,
            (sentinel.annotation2, 'bar'): 4,
        }[(annotation, field)]
    mock_get_annotation_field.side_effect = _mock_get_annotation_field

    assert filter_annotations(
        [
            sentinel.annotation0,
            sentinel.annotation1,
            sentinel.annotation2,
        ],
        filter_fields={'foo': 3, 'bar': 4}
    ) == []


@patch('concrete.util.metadata.get_annotation_field')
def test_filter_annotations_multiple(mock_get_annotation_field):
    def _mock_get_annotation_field(annotation, field):
        return {
            (sentinel.annotation0, 'foo'): 3,
            (sentinel.annotation1, 'foo'): 3,
            (sentinel.annotation2, 'foo'): 3,
            (sentinel.annotation0, 'bar'): 4,
            (sentinel.annotation1, 'bar'): 3,
            (sentinel.annotation2, 'bar'): 4,
        }[(annotation, field)]
    mock_get_annotation_field.side_effect = _mock_get_annotation_field

    assert filter_annotations(
        [
            sentinel.annotation0,
            sentinel.annotation1,
            sentinel.annotation2,
        ],
        filter_fields={'foo': 3, 'bar': 4}
    ) == [sentinel.annotation0, sentinel.annotation2]


@patch('concrete.util.metadata.get_annotation_field')
def test_filter_annotations_multiple_reverse(mock_get_annotation_field):
    def _mock_get_annotation_field(annotation, field):
        return {
            (sentinel.annotation0, 'foo'): 3,
            (sentinel.annotation1, 'foo'): 3,
            (sentinel.annotation2, 'foo'): 3,
            (sentinel.annotation3, 'foo'): 3,
            (sentinel.annotation0, 'bar'): 4,
            (sentinel.annotation1, 'bar'): 3,
            (sentinel.annotation2, 'bar'): 4,
            (sentinel.annotation3, 'bar'): 4,
        }[(annotation, field)]
    mock_get_annotation_field.side_effect = _mock_get_annotation_field

    assert filter_annotations(
        [
            sentinel.annotation0,
            sentinel.annotation1,
            sentinel.annotation2,
            sentinel.annotation3,
        ],
        filter_fields={'foo': 3, 'bar': 4},
        sort_reverse=True
    ) == [sentinel.annotation3, sentinel.annotation2, sentinel.annotation0]


@patch('concrete.util.metadata.get_annotation_field')
def test_filter_annotations_multiple_sort(mock_get_annotation_field):
    def _mock_get_annotation_field(annotation, field):
        return {
            (sentinel.annotation0, 'foo'): 3,
            (sentinel.annotation1, 'foo'): 3,
            (sentinel.annotation2, 'foo'): 3,
            (sentinel.annotation3, 'foo'): 3,
            (sentinel.annotation0, 'bar'): 4,
            (sentinel.annotation1, 'bar'): 3,
            (sentinel.annotation2, 'bar'): 4,
            (sentinel.annotation3, 'bar'): 4,
            (sentinel.annotation0, 'baz'): 2,
            (sentinel.annotation1, 'baz'): 0,
            (sentinel.annotation2, 'baz'): 1,
            (sentinel.annotation3, 'baz'): 3,
        }[(annotation, field)]
    mock_get_annotation_field.side_effect = _mock_get_annotation_field

    assert filter_annotations(
        [
            sentinel.annotation0,
            sentinel.annotation1,
            sentinel.annotation2,
            sentinel.annotation3,
        ],
        filter_fields={'foo': 3, 'bar': 4},
        sort_field='baz'
    ) == [sentinel.annotation2, sentinel.annotation0, sentinel.annotation3]


@patch('concrete.util.metadata.get_annotation_field')
def test_filter_annotations_multiple_sort_reverse(mock_get_annotation_field):
    def _mock_get_annotation_field(annotation, field):
        return {
            (sentinel.annotation0, 'foo'): 3,
            (sentinel.annotation1, 'foo'): 3,
            (sentinel.annotation2, 'foo'): 3,
            (sentinel.annotation3, 'foo'): 3,
            (sentinel.annotation0, 'bar'): 4,
            (sentinel.annotation1, 'bar'): 3,
            (sentinel.annotation2, 'bar'): 4,
            (sentinel.annotation3, 'bar'): 4,
            (sentinel.annotation0, 'baz'): 2,
            (sentinel.annotation1, 'baz'): 0,
            (sentinel.annotation2, 'baz'): 1,
            (sentinel.annotation3, 'baz'): 3,
        }[(annotation, field)]
    mock_get_annotation_field.side_effect = _mock_get_annotation_field

    assert filter_annotations(
        [
            sentinel.annotation0,
            sentinel.annotation1,
            sentinel.annotation2,
            sentinel.annotation3,
        ],
        filter_fields={'foo': 3, 'bar': 4},
        sort_field='baz',
        sort_reverse=True
    ) == [sentinel.annotation3, sentinel.annotation0, sentinel.annotation2]


@patch('concrete.util.metadata.get_annotation_field')
def test_filter_annotations_multiple_raise(mock_get_annotation_field):
    def _mock_get_annotation_field(annotation, field):
        return {
            (sentinel.annotation0, 'foo'): 3,
            (sentinel.annotation1, 'foo'): 3,
            (sentinel.annotation2, 'foo'): 3,
            (sentinel.annotation0, 'bar'): 4,
            (sentinel.annotation1, 'bar'): 3,
            (sentinel.annotation2, 'bar'): 4,
        }[(annotation, field)]
    mock_get_annotation_field.side_effect = _mock_get_annotation_field

    with raises(MultipleAnnotationsError):
        filter_annotations(
            [
                sentinel.annotation0,
                sentinel.annotation1,
                sentinel.annotation2,
            ],
            filter_fields={'foo': 3, 'bar': 4},
            action_if_multiple='raise'
        )


@patch('concrete.util.metadata.get_annotation_field')
def test_filter_annotations_zero_raise(mock_get_annotation_field):
    def _mock_get_annotation_field(annotation, field):
        return {
            (sentinel.annotation0, 'foo'): 3,
            (sentinel.annotation1, 'foo'): 3,
            (sentinel.annotation2, 'foo'): 4,
            (sentinel.annotation0, 'bar'): 3,
            (sentinel.annotation1, 'bar'): 3,
            (sentinel.annotation2, 'bar'): 4,
        }[(annotation, field)]
    mock_get_annotation_field.side_effect = _mock_get_annotation_field

    with raises(ZeroAnnotationsError):
        filter_annotations(
            [
                sentinel.annotation0,
                sentinel.annotation1,
                sentinel.annotation2,
            ],
            filter_fields={'foo': 3, 'bar': 4},
            action_if_zero='raise'
        )


@patch('concrete.util.metadata.get_annotation_field')
def test_filter_annotations_zero_raise_with_multiple(
        mock_get_annotation_field):
    def _mock_get_annotation_field(annotation, field):
        return {
            (sentinel.annotation0, 'foo'): 3,
            (sentinel.annotation1, 'foo'): 3,
            (sentinel.annotation2, 'foo'): 3,
            (sentinel.annotation0, 'bar'): 4,
            (sentinel.annotation1, 'bar'): 3,
            (sentinel.annotation2, 'bar'): 4,
        }[(annotation, field)]
    mock_get_annotation_field.side_effect = _mock_get_annotation_field

    assert filter_annotations(
        [
            sentinel.annotation0,
            sentinel.annotation1,
            sentinel.annotation2,
        ],
        filter_fields={'foo': 3, 'bar': 4},
        action_if_zero='raise'
    ) == [sentinel.annotation0, sentinel.annotation2]


@patch('concrete.util.metadata.get_annotation_field')
def test_filter_annotations_multiple_raise_with_zero(
        mock_get_annotation_field):
    def _mock_get_annotation_field(annotation, field):
        return {
            (sentinel.annotation0, 'foo'): 3,
            (sentinel.annotation1, 'foo'): 3,
            (sentinel.annotation2, 'foo'): 4,
            (sentinel.annotation0, 'bar'): 3,
            (sentinel.annotation1, 'bar'): 3,
            (sentinel.annotation2, 'bar'): 4,
        }[(annotation, field)]
    mock_get_annotation_field.side_effect = _mock_get_annotation_field

    assert filter_annotations(
        [
            sentinel.annotation0,
            sentinel.annotation1,
            sentinel.annotation2,
        ],
        filter_fields={'foo': 3, 'bar': 4},
        action_if_multiple='raise'
    ) == []


@patch('concrete.util.metadata.get_annotation_field')
def test_filter_annotations_zero_raise_with_one(mock_get_annotation_field):
    def _mock_get_annotation_field(annotation, field):
        return {
            (sentinel.annotation0, 'foo'): 3,
            (sentinel.annotation1, 'foo'): 3,
            (sentinel.annotation2, 'foo'): 4,
            (sentinel.annotation0, 'bar'): 3,
            (sentinel.annotation1, 'bar'): 4,
            (sentinel.annotation2, 'bar'): 4,
        }[(annotation, field)]
    mock_get_annotation_field.side_effect = _mock_get_annotation_field

    assert filter_annotations(
        [
            sentinel.annotation0,
            sentinel.annotation1,
            sentinel.annotation2,
        ],
        filter_fields={'foo': 3, 'bar': 4}
    ) == [sentinel.annotation1]


@patch('concrete.util.metadata.get_annotation_field')
def test_filter_annotations_multiple_raise_with_one(mock_get_annotation_field):
    def _mock_get_annotation_field(annotation, field):
        return {
            (sentinel.annotation0, 'foo'): 3,
            (sentinel.annotation1, 'foo'): 3,
            (sentinel.annotation2, 'foo'): 4,
            (sentinel.annotation0, 'bar'): 3,
            (sentinel.annotation1, 'bar'): 4,
            (sentinel.annotation2, 'bar'): 4,
        }[(annotation, field)]
    mock_get_annotation_field.side_effect = _mock_get_annotation_field

    assert filter_annotations(
        [
            sentinel.annotation0,
            sentinel.annotation1,
            sentinel.annotation2,
        ],
        filter_fields={'foo': 3, 'bar': 4}
    ) == [sentinel.annotation1]


@patch('concrete.util.metadata.get_annotation_field')
def test_filter_annotations_multiple_first(
        mock_get_annotation_field):
    def _mock_get_annotation_field(annotation, field):
        return {
            (sentinel.annotation0, 'foo'): 3,
            (sentinel.annotation1, 'foo'): 3,
            (sentinel.annotation2, 'foo'): 3,
            (sentinel.annotation0, 'bar'): 4,
            (sentinel.annotation1, 'bar'): 3,
            (sentinel.annotation2, 'bar'): 4,
        }[(annotation, field)]
    mock_get_annotation_field.side_effect = _mock_get_annotation_field

    assert filter_annotations(
        [
            sentinel.annotation0,
            sentinel.annotation1,
            sentinel.annotation2,
        ],
        filter_fields={'foo': 3, 'bar': 4},
        action_if_multiple='first'
    ) == [sentinel.annotation0]


@patch('concrete.util.metadata.get_annotation_field')
def test_filter_annotations_multiple_last(
        mock_get_annotation_field):
    def _mock_get_annotation_field(annotation, field):
        return {
            (sentinel.annotation0, 'foo'): 3,
            (sentinel.annotation1, 'foo'): 3,
            (sentinel.annotation2, 'foo'): 3,
            (sentinel.annotation0, 'bar'): 4,
            (sentinel.annotation1, 'bar'): 3,
            (sentinel.annotation2, 'bar'): 4,
        }[(annotation, field)]
    mock_get_annotation_field.side_effect = _mock_get_annotation_field

    assert filter_annotations(
        [
            sentinel.annotation0,
            sentinel.annotation1,
            sentinel.annotation2,
        ],
        filter_fields={'foo': 3, 'bar': 4},
        action_if_multiple='last'
    ) == [sentinel.annotation2]


@patch('concrete.util.metadata.get_annotation_field')
def test_filter_annotations_multiple_sort_first(mock_get_annotation_field):
    def _mock_get_annotation_field(annotation, field):
        return {
            (sentinel.annotation0, 'foo'): 3,
            (sentinel.annotation1, 'foo'): 3,
            (sentinel.annotation2, 'foo'): 3,
            (sentinel.annotation3, 'foo'): 3,
            (sentinel.annotation0, 'bar'): 4,
            (sentinel.annotation1, 'bar'): 3,
            (sentinel.annotation2, 'bar'): 4,
            (sentinel.annotation3, 'bar'): 4,
            (sentinel.annotation0, 'baz'): 2,
            (sentinel.annotation1, 'baz'): 0,
            (sentinel.annotation2, 'baz'): 1,
            (sentinel.annotation3, 'baz'): 3,
        }[(annotation, field)]
    mock_get_annotation_field.side_effect = _mock_get_annotation_field

    assert filter_annotations(
        [
            sentinel.annotation0,
            sentinel.annotation1,
            sentinel.annotation2,
            sentinel.annotation3,
        ],
        filter_fields={'foo': 3, 'bar': 4},
        sort_field='baz',
        action_if_multiple='first'
    ) == [sentinel.annotation2]


@patch('concrete.util.metadata.get_annotation_field')
def test_filter_annotations_multiple_sort_last(mock_get_annotation_field):
    def _mock_get_annotation_field(annotation, field):
        return {
            (sentinel.annotation0, 'foo'): 3,
            (sentinel.annotation1, 'foo'): 3,
            (sentinel.annotation2, 'foo'): 3,
            (sentinel.annotation3, 'foo'): 3,
            (sentinel.annotation0, 'bar'): 4,
            (sentinel.annotation1, 'bar'): 3,
            (sentinel.annotation2, 'bar'): 4,
            (sentinel.annotation3, 'bar'): 4,
            (sentinel.annotation0, 'baz'): 2,
            (sentinel.annotation1, 'baz'): 0,
            (sentinel.annotation2, 'baz'): 1,
            (sentinel.annotation3, 'baz'): 3,
        }[(annotation, field)]
    mock_get_annotation_field.side_effect = _mock_get_annotation_field

    assert filter_annotations(
        [
            sentinel.annotation0,
            sentinel.annotation1,
            sentinel.annotation2,
            sentinel.annotation3,
        ],
        filter_fields={'foo': 3, 'bar': 4},
        sort_field='baz',
        action_if_multiple='last'
    ) == [sentinel.annotation3]


@patch('concrete.util.metadata.get_annotation_field')
def test_filter_annotations_multiple_sort_reverse_first(
        mock_get_annotation_field):
    def _mock_get_annotation_field(annotation, field):
        return {
            (sentinel.annotation0, 'foo'): 3,
            (sentinel.annotation1, 'foo'): 3,
            (sentinel.annotation2, 'foo'): 3,
            (sentinel.annotation3, 'foo'): 3,
            (sentinel.annotation0, 'bar'): 4,
            (sentinel.annotation1, 'bar'): 3,
            (sentinel.annotation2, 'bar'): 4,
            (sentinel.annotation3, 'bar'): 4,
            (sentinel.annotation0, 'baz'): 2,
            (sentinel.annotation1, 'baz'): 0,
            (sentinel.annotation2, 'baz'): 1,
            (sentinel.annotation3, 'baz'): 3,
        }[(annotation, field)]
    mock_get_annotation_field.side_effect = _mock_get_annotation_field

    assert filter_annotations(
        [
            sentinel.annotation0,
            sentinel.annotation1,
            sentinel.annotation2,
            sentinel.annotation3,
        ],
        filter_fields={'foo': 3, 'bar': 4},
        sort_field='baz',
        sort_reverse=True,
        action_if_multiple='first'
    ) == [sentinel.annotation3]


@patch('concrete.util.metadata.get_annotation_field')
def test_filter_annotations_multiple_sort_reverse_last(
        mock_get_annotation_field):
    def _mock_get_annotation_field(annotation, field):
        return {
            (sentinel.annotation0, 'foo'): 3,
            (sentinel.annotation1, 'foo'): 3,
            (sentinel.annotation2, 'foo'): 3,
            (sentinel.annotation3, 'foo'): 3,
            (sentinel.annotation0, 'bar'): 4,
            (sentinel.annotation1, 'bar'): 3,
            (sentinel.annotation2, 'bar'): 4,
            (sentinel.annotation3, 'bar'): 4,
            (sentinel.annotation0, 'baz'): 2,
            (sentinel.annotation1, 'baz'): 0,
            (sentinel.annotation2, 'baz'): 1,
            (sentinel.annotation3, 'baz'): 3,
        }[(annotation, field)]
    mock_get_annotation_field.side_effect = _mock_get_annotation_field

    assert filter_annotations(
        [
            sentinel.annotation0,
            sentinel.annotation1,
            sentinel.annotation2,
            sentinel.annotation3,
        ],
        filter_fields={'foo': 3, 'bar': 4},
        sort_field='baz',
        sort_reverse=True,
        action_if_multiple='last'
    ) == [sentinel.annotation2]


@patch('concrete.util.metadata.filter_annotations')
def test_filter_annotations_json(mock_filter_annotations):
    mock_filter_annotations.side_effect = [sentinel.return_value]
    assert filter_annotations_json(
        sentinel.annotations,
        '{"foo": 47, "baz": ["hello", "world"]}'
    ) == sentinel.return_value
    mock_filter_annotations.assert_called_once_with(
        sentinel.annotations,
        foo=47,
        baz=['hello', 'world'],
    )


def test_tool_to_filter():
    assert tool_to_filter(None, None) is None
    assert tool_to_filter(None, sentinel.explicit_filter) == sentinel.explicit_filter

    annotation_filter = tool_to_filter(sentinel.tool, None)
    annotations = [
        Mock(metadata=Mock(tool=sentinel.tool)),
        Mock(metadata=Mock(tool=sentinel.other_tool)),
        Mock(metadata=Mock(tool=sentinel.tool)),
    ]
    assert annotation_filter(annotations) == [annotations[0], annotations[2]]

    with raises(ValueError):
        tool_to_filter(sentinel.tool, sentinel.explicit_filter)
