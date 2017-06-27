from __future__ import unicode_literals
from datetime import datetime
import json
import logging


EPOCH = datetime.utcfromtimestamp(0)


class ZeroAnnotationsError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class MultipleAnnotationsError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def datetime_to_timestamp(dt):
    '''
    Given time-zone--unaware datetime object representing date and time
    in UTC, return corresponding Concrete timestamp.

    Args:
        dt(datetime): time-zone--unaware datetime object representing
        date and time (in UTC) to convert

    Source:
    http://stackoverflow.com/questions/6999726/how-can-i-convert-a-datetime-object-to-milliseconds-since-epoch-unix-time-in-p
    '''
    return int((dt - EPOCH).total_seconds())


def timestamp_to_datetime(timestamp):
    '''
    Given Concrete timestamp, return corresponding time-zone--unaware
    datetime object representing date and time in UTC.

    Args:
        timestamp(int): Concrete timestamp (integer representing
            seconds since the epoch in UTC) representing date and time
            to convert

    Source:
    https://stackoverflow.com/questions/3694487/initialize-a-datetime-object-with-seconds-since-epoch
    '''
    return datetime.utcfromtimestamp(timestamp)


def now_timestamp():
    '''
    Return timestamp representing the current time.
    '''
    return datetime_to_timestamp(datetime.now())


def get_index_of_tool(lst_of_conc, tool):
    """Return the index of the object in the provided list
    whose tool name matches tool.

    If tool is None, return the first valid index into `lst_of_conc`.

    This returns -1 if:
      * `lst_of_conc` is None, or
      * `lst_of_conc` has no entries, or
      * no object in `lst_of_conc` matches `tool`.

    Args:

    - `lst_of_conc`: A list of Concrete objects, each of which
      has a `.metadata` field.
    - `tool`: A tool name to match.
    """
    idx = -1
    if lst_of_conc is not None and len(lst_of_conc) > 0:
        if tool is not None:
            for (cidx, obj) in enumerate(lst_of_conc):
                if obj.metadata.tool == tool:
                    idx = cidx
                    break
        else:
            idx = 0
    return idx


def get_annotation_field(annotation, field):
    '''
    Return requested field of annotation metadata.

    Args:
        annotation: object containing a `metadata` field of
            type :class:`..metadata.ttypes.AnnotationMetadata`.
        field: name of metadata field: kBest, timestamp, or tool.

    Returns:
        value of requested field in annotation metadata.
    '''
    if field == 'kBest':
        return annotation.metadata.kBest
    elif field == 'timestamp':
        return annotation.metadata.timestamp
    elif field == 'tool':
        return annotation.metadata.tool
    else:
        raise ValueError('unrecognized field {}'.format(field))


def filter_annotations(annotations,
                       filter_fields=None,
                       sort_field=None,
                       sort_reverse=False,
                       action_if_multiple='pass',
                       action_if_zero='pass'):
    '''
    Return filtered and/or re-ordered list of annotations, that is,
    objects containing a `metadata` field of type AnnotationMetadata.
    The default behavior is to do no filtering (or re-ordering),
    returning an exact copy of annotations.

    Args:
        annotations (list): original list of annotations (objects
            containing a `metadata` field of type
            :class:`..metadata.ttypes.AnnotationMetadata`).
            This list is not modified.
        filter_fields (dict): dict of fields and their desired values
            by which to filter annotations (keep annotations whose
            field `FIELD` equals `VALUE` for all `FIELD:
            VALUE`) entries).  Default: keep all annotations.
            See :func:`get_annotation_field` for valid fields.
        sort_field (str): field by which to re-order annotations.
            Default: do not re-order annotations.
        sort_reverse (bool): True to reverse order of annotations
            (after sorting, if any).
        action_if_multiple (str): action to take if, after filtering,
            there is more than one annotation left.  'pass' to
            return all filtered and re-ordered annotations, 'raise' to
            raise an exception of type `MultipleAnnotationsError`,
            'first' to return a list containing the first annotation
            after filtering and re-ordering, or 'last' to return a list
            containing the last annotation after filtering and
            re-ordering.
        action_if_zero (str): action to take if, after filtering, there
            are no annotations left.  'pass' to return an empty list,
            'raise' to raise an exception of type
            `ZeroAnnotationsError`.

    Returns:
        filtered and/or re-ordered list of annotations
    '''
    annotations = list(annotations)

    if filter_fields:
        annotations = [
            a for a in annotations
            if all(
                get_annotation_field(a, field) == value
                for (field, value) in filter_fields.items()
            )
        ]

    if sort_field:
        annotations = sorted(
            annotations,
            key=lambda a: get_annotation_field(a, sort_field))

    if sort_reverse:
        annotations = annotations[::-1]

    if len(annotations) == 0:
        if action_if_zero == 'raise':
            raise ZeroAnnotationsError()
        elif action_if_zero == 'pass':
            pass
        else:
            raise ValueError('unknown action_if_zero value {}'.format(
                action_if_zero))
    elif len(annotations) > 1:
        if action_if_multiple == 'raise':
            raise MultipleAnnotationsError()
        elif action_if_multiple == 'pass':
            pass
        elif action_if_multiple == 'first':
            annotations = [annotations[0]]
        elif action_if_multiple == 'last':
            annotations = [annotations[-1]]
        else:
            raise ValueError('unknown action_if_multiple value {}'.format(
                action_if_multiple))

    return annotations


def filter_annotations_json(annotations, kwargs_json):
    '''
    Call :func:`filter_annotations` on `annotations`, sending it
    keyword arguments from the JSON-encoded dictionary
    `kwargs_json`.

    Args:
        annotations (list): original list of annotations (objects
            containing a `metadata` field of type
            :class:`..metadata.ttypes.AnnotationMetadata`).
            This list is not modified.
        kwargs_json (str): JSON-encoded dictionary of keyword
            arguments to be passed to :func:`filter_annotations`.

    Returns:
        `annotations` filtered by :func:`filter_annotations` according
        to provided JSON-encoded keyword arguments.
    '''

    return filter_annotations(annotations, **json.loads(kwargs_json))


def filter_unnone(annotation_filter):
    '''
    If annotation_filter is None, return no-op filter.

    Args:
        annotation_filter (func): function that takes a list of
            annotations and returns a filtered (and/or re-ordered)
            list of annotations

    Returns:
        function that takes a list of annotations and returns a
        filtered (and/or re-ordered) list of annotations.
    '''
    if annotation_filter is None:
        return lambda annotations: annotations
    else:
        return annotation_filter


def tool_to_filter(tool, explicit_filter=None):
    '''
    Given tool name (deprecated way to filter annotations) or None,
    and an explicit annotation filter function or None, return an
    annotation filter function representing whichever is not None
    (and raise ValueError if both are not None).

    Args:
        tool (str): name of tool to filter by, or None
        explicit_filter (func): function taking a list of annotations
            as input and returning a sub-list (possibly re-ordered)
            as output, or None

    Returns:
        Function taking a list of annotations as input and either
        applying `explicit_filter` to them and returning its output
        or filtering them by tool `tool` and returning that filtered
        list.  If both `tool` and `explicit_filter` are not None,
        raise ValueError.
    '''
    if tool is None:
        return explicit_filter
    else:
        logging.warning('tool is deprecated; please pass filter instead')
        if explicit_filter is None:
            return lambda annotations: filter_annotations(
                annotations,
                filter_fields=dict(tool=tool))
        else:
            raise ValueError('tool and filter cannot be both be specified')
