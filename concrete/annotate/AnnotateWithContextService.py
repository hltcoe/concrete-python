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
import concrete.services.Service
import logging
from .ttypes import *
from thrift.Thrift import TProcessor
from thrift.transport import TTransport
all_structs = []


class Iface(concrete.services.Service.Iface):
    """
    A service that provides an alternative to Annotate,
    with the ability to pass along an additional Context
    parameter that conveys additional information about the
    Communication.

    """
    def annotate(self, original, context):
        """
        Takes a Communication and a Context as input
        and returns a new one as output.

        It is up to the implementing service to verify that
        the input communication is valid, as well as interpret
        the Context in an appropriate manner.

        Can throw a ConcreteThriftException upon error
        (invalid input, analytic exception, etc.).

        Parameters:
         - original
         - context

        """
        pass


class Client(concrete.services.Service.Client, Iface):
    """
    A service that provides an alternative to Annotate,
    with the ability to pass along an additional Context
    parameter that conveys additional information about the
    Communication.

    """
    def __init__(self, iprot, oprot=None):
        concrete.services.Service.Client.__init__(self, iprot, oprot)

    def annotate(self, original, context):
        """
        Takes a Communication and a Context as input
        and returns a new one as output.

        It is up to the implementing service to verify that
        the input communication is valid, as well as interpret
        the Context in an appropriate manner.

        Can throw a ConcreteThriftException upon error
        (invalid input, analytic exception, etc.).

        Parameters:
         - original
         - context

        """
        self.send_annotate(original, context)
        return self.recv_annotate()

    def send_annotate(self, original, context):
        self._oprot.writeMessageBegin('annotate', TMessageType.CALL, self._seqid)
        args = annotate_args()
        args.original = original
        args.context = context
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def recv_annotate(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        result = annotate_result()
        result.read(iprot)
        iprot.readMessageEnd()
        if result.success is not None:
            return result.success
        if result.ex is not None:
            raise result.ex
        raise TApplicationException(TApplicationException.MISSING_RESULT, "annotate failed: unknown result")


class Processor(concrete.services.Service.Processor, Iface, TProcessor):
    def __init__(self, handler):
        concrete.services.Service.Processor.__init__(self, handler)
        self._processMap["annotate"] = Processor.process_annotate
        self._on_message_begin = None

    def on_message_begin(self, func):
        self._on_message_begin = func

    def process(self, iprot, oprot):
        (name, type, seqid) = iprot.readMessageBegin()
        if self._on_message_begin:
            self._on_message_begin(name, type, seqid)
        if name not in self._processMap:
            iprot.skip(TType.STRUCT)
            iprot.readMessageEnd()
            x = TApplicationException(TApplicationException.UNKNOWN_METHOD, 'Unknown function %s' % (name))
            oprot.writeMessageBegin(name, TMessageType.EXCEPTION, seqid)
            x.write(oprot)
            oprot.writeMessageEnd()
            oprot.trans.flush()
            return
        else:
            self._processMap[name](self, seqid, iprot, oprot)
        return True

    def process_annotate(self, seqid, iprot, oprot):
        args = annotate_args()
        args.read(iprot)
        iprot.readMessageEnd()
        result = annotate_result()
        try:
            result.success = self._handler.annotate(args.original, args.context)
            msg_type = TMessageType.REPLY
        except TTransport.TTransportException:
            raise
        except concrete.exceptions.ttypes.ConcreteThriftException as ex:
            msg_type = TMessageType.REPLY
            result.ex = ex
        except TApplicationException as ex:
            logging.exception('TApplication exception in handler')
            msg_type = TMessageType.EXCEPTION
            result = ex
        except Exception:
            logging.exception('Unexpected exception in handler')
            msg_type = TMessageType.EXCEPTION
            result = TApplicationException(TApplicationException.INTERNAL_ERROR, 'Internal error')
        oprot.writeMessageBegin("annotate", msg_type, seqid)
        result.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

# HELPER FUNCTIONS AND STRUCTURES


class annotate_args(object):
    """
    Attributes:
     - original
     - context

    """


    def __init__(self, original=None, context=None,):
        self.original = original
        self.context = context

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
                if ftype == TType.STRUCT:
                    self.original = concrete.communication.ttypes.Communication()
                    self.original.read(iprot)
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.STRUCT:
                    self.context = concrete.context.ttypes.Context()
                    self.context.read(iprot)
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
        oprot.writeStructBegin('annotate_args')
        if self.original is not None:
            oprot.writeFieldBegin('original', TType.STRUCT, 1)
            self.original.write(oprot)
            oprot.writeFieldEnd()
        if self.context is not None:
            oprot.writeFieldBegin('context', TType.STRUCT, 2)
            self.context.write(oprot)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)
all_structs.append(annotate_args)
annotate_args.thrift_spec = (
    None,  # 0
    (1, TType.STRUCT, 'original', [concrete.communication.ttypes.Communication, None], None, ),  # 1
    (2, TType.STRUCT, 'context', [concrete.context.ttypes.Context, None], None, ),  # 2
)


class annotate_result(object):
    """
    Attributes:
     - success
     - ex

    """


    def __init__(self, success=None, ex=None,):
        self.success = success
        self.ex = ex

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 0:
                if ftype == TType.STRUCT:
                    self.success = concrete.communication.ttypes.Communication()
                    self.success.read(iprot)
                else:
                    iprot.skip(ftype)
            elif fid == 1:
                if ftype == TType.STRUCT:
                    self.ex = concrete.exceptions.ttypes.ConcreteThriftException.read(iprot)
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
        oprot.writeStructBegin('annotate_result')
        if self.success is not None:
            oprot.writeFieldBegin('success', TType.STRUCT, 0)
            self.success.write(oprot)
            oprot.writeFieldEnd()
        if self.ex is not None:
            oprot.writeFieldBegin('ex', TType.STRUCT, 1)
            self.ex.write(oprot)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)
all_structs.append(annotate_result)
annotate_result.thrift_spec = (
    (0, TType.STRUCT, 'success', [concrete.communication.ttypes.Communication, None], None, ),  # 0
    (1, TType.STRUCT, 'ex', [concrete.exceptions.ttypes.ConcreteThriftException, None], None, ),  # 1
)
fix_spec(all_structs)
del all_structs
