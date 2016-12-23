"""Convert Concrete objects to JSON strings
"""

import json

from thrift import TSerialization
from thrift.protocol import TJSONProtocol

from concrete.util import (
    read_communication_from_file,
    read_tokenlattice_from_file,
)


def communication_file_to_json(communication_filename, remove_timestamps=False,
                               remove_uuids=False):
    """Get a "pretty-printed" JSON string representation for a Communication

    Args:

    - `communication_filename`: String specifying Communication filename
    - `remove_uuids`: Boolean flag indicating if Concrete UUIDs should be
                      removed

    Returns:

    - A string containing a "pretty-printed" JSON representation of the
      Communication
    """
    comm = read_communication_from_file(communication_filename)
    return thrift_to_json(comm, remove_timestamps=remove_timestamps,
                          remove_uuids=remove_uuids)


def tokenlattice_file_to_json(toklat_filename):
    """Get a "pretty-printed" JSON string representation for a TokenLattice

    Args:

    - `toklat_filename`: String specifying TokenLattice filename

    Returns:

    - A string containing a "pretty-printed" JSON representation of the
      TokenLattice
    """
    toklat = read_tokenlattice_from_file(toklat_filename)
    return thrift_to_json(toklat)


def get_json_object_without_timestamps(json_object):
    """Create a copy of a JSON object created by json.loads(), with all
    representations of Concrete Metadata timestamps (dictionary keys
    with value 'timestamp') recursively removed.

    Args:

    - `json_object`: A Python data structure created from a JSON string by
                     json.loads

    Returns:

    - A copy of the input data structure with all timestamp objects removed
    """
    if type(json_object) is list:
        new_json_object = [get_json_object_without_timestamps(obj)
                           for obj in json_object]
    elif type(json_object) is dict:
        new_json_object = {}
        for k, v in json_object.iteritems():
            if k != "timestamp":
                new_json_object[k] = get_json_object_without_timestamps(v)
    else:
        new_json_object = json_object

    return new_json_object


def get_json_object_without_uuids(json_object):
    """Create a copy of a JSON object created by json.loads(), with all
    representations of Concrete UUIDs (dictionaries containing a
    'uuidString' key) recursively removed.

    Args:

    - `json_object`: A Python data structure created from a JSON string by
                     json.loads

    Returns:

    - A copy of the input data structure with all UUID objects removed
    """
    if type(json_object) is list:
        new_json_object = [get_json_object_without_uuids(obj)
                           for obj in json_object
                           if type(obj) is not dict or 'uuidString' not in obj]
    elif type(json_object) is dict:
        new_json_object = {}
        for k, v in json_object.iteritems():
            if type(v) is not dict or 'uuidString' not in v:
                new_json_object[k] = get_json_object_without_uuids(v)
    else:
        new_json_object = json_object

    return new_json_object


def thrift_to_json(tobj, remove_timestamps=False, remove_uuids=False):
    """Get a "pretty-printed" JSON string representation for a Thrift object

    Args:

    - `tobj`: A Thrift object
    - `remove_uuids`: Boolean flag indicating if Concrete UUIDs should be
                      removed

    Returns:

    - A string containing a "pretty-printed" JSON representation of the Thrift
      object
    """
    thrift_json_string = TSerialization.serialize(
        tobj, TJSONProtocol.TSimpleJSONProtocolFactory())
    thrift_json = json.loads(thrift_json_string)

    if remove_timestamps:
        thrift_json = get_json_object_without_timestamps(thrift_json)
    if remove_uuids:
        thrift_json = get_json_object_without_uuids(thrift_json)

    return json.dumps(thrift_json, indent=2, separators=(',', ': '),
                      ensure_ascii=False, sort_keys=True)
