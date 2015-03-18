"""Convert Concrete objects to JSON strings
"""

import json

from thrift import TSerialization
from thrift.protocol import TJSONProtocol

from concrete.util import read_communication_from_file, read_tokenlattice_from_file


def communication_file_to_json(communication_filename):
    """Get a "pretty-printed" JSON string representation for a Communication

    Args:

    - `communication_filename`: String specifying Communication filename

    Returns:

    - A string containing a "pretty-printed" JSON representation of the Communication
    """
    comm = read_communication_from_file(communication_filename)
    return thrift_to_json(comm)

def tokenlattice_file_to_json(toklat_filename):
    """Get a "pretty-printed" JSON string representation for a TokenLattice

    Args:

    - `toklat_filename`: String specifying TokenLattice filename

    Returns:

    - A string containing a "pretty-printed" JSON representation of the TokenLattice
    """
    toklat = read_tokenlattice_from_file(toklat_filename)
    return thrift_to_json(toklat)


def thrift_to_json(tobj):
    """Get a "pretty-printed" JSON string representation for a Thrift object

    Args:

    - `tobj`: A Thrift object

    Returns:

    - A string containing a "pretty-printed" JSON representation of the Thrift object
    """
    thrift_json_string = TSerialization.serialize(tobj, TJSONProtocol.TSimpleJSONProtocolFactory())
    thrift_json = json.loads(thrift_json_string)
    return json.dumps(thrift_json, indent=2, separators=(',', ': '), ensure_ascii=False, sort_keys=True)
