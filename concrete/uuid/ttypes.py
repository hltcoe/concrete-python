# -*- coding: utf-8 -*-
#
# Autogenerated by Thrift Compiler (0.18.0)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py:coding=utf-8
#

from thrift.Thrift import TType, TMessageType, TFrozenDict, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
from thrift.TRecursive import fix_spec

import sys

from thrift.transport import TTransport
all_structs = []


class UUID(object):
    """
    Attributes:
     - uuidString: A string representation of a UUID, in the format of:
    <pre>
    550e8400-e29b-41d4-a716-446655440000
    </pre>

    """


    def __init__(self, uuidString=None,):
        self.uuidString = uuidString

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRING:
                    self.uuidString = iprot.readString().decode('utf-8', errors='replace') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('UUID')
        if self.uuidString is not None:
            oprot.writeFieldBegin('uuidString', TType.STRING, 1)
            oprot.writeString(self.uuidString.encode('utf-8') if sys.version_info[0] == 2 else self.uuidString)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        if self.uuidString is None:
            raise TProtocolException(message='Required field uuidString is unset!')
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)
all_structs.append(UUID)
UUID.thrift_spec = (
    None,  # 0
    (1, TType.STRING, 'uuidString', 'UTF8', None, ),  # 1
)
fix_spec(all_structs)
del all_structs
