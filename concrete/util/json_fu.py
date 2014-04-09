"""
"""

import json

from thrift import TSerialization
from thrift.protocol import TJSONProtocol

from concrete.util import read_communication_from_file


def concrete2json(communication_filename):
    """
    Takes a Communication instance, returns a JSON string with the
    information in that Communication.
    """
    comm = read_communication_from_file(communication_filename)
    comm_json_string = TSerialization.serialize(comm, TJSONProtocol.TSimpleJSONProtocolFactory())
    comm_json = json.loads(comm_json_string)
    return json.dumps(comm_json, indent=2, separators=(',', ': '), ensure_ascii=False, sort_keys=True)
