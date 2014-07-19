"""
"""

import json

from thrift import TSerialization
from thrift.protocol import TJSONProtocol

from concrete.util import read_communication_from_file, read_tokenlattice_from_file


def communication_file_to_json(communication_filename):
    """
    Takes a Communication filename, deserializes Communication from
    file, returns a JSON string with the information in that
    Communication.
    """
    comm = read_communication_from_file(communication_filename)
    return thrift_to_json(comm)

def tokenlattice_file_to_json(toklat_filename):
    """
    Takes a Communication filename, deserializes Communication from
    file, returns a JSON string with the information in that
    Communication.
    """
    toklat = read_tokenlattice_from_file(toklat_filename)
    return thrift_to_json(toklat)


def thrift_to_json(tobj):
    """
    Takes a Thrift instance, returns a JSON string with the
    information in that Thrift object.
    """
    thrift_json_string = TSerialization.serialize(tobj, TJSONProtocol.TSimpleJSONProtocolFactory())
    thrift_json = json.loads(thrift_json_string)
    return json.dumps(thrift_json, indent=2, separators=(',', ': '), ensure_ascii=False, sort_keys=True)
