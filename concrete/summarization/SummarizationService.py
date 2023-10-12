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
    def summarize(self, query):
        """
        Parameters:
         - query

        """
        pass

    def getCapabilities(self):
        pass


class Client(concrete.services.Service.Client, Iface):
    def __init__(self, iprot, oprot=None):
        concrete.services.Service.Client.__init__(self, iprot, oprot)

    def summarize(self, query):
        """
        Parameters:
         - query

        """
        self.send_summarize(query)
        return self.recv_summarize()

    def send_summarize(self, query):
        self._oprot.writeMessageBegin('summarize', TMessageType.CALL, self._seqid)
        args = summarize_args()
        args.query = query
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def recv_summarize(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        result = summarize_result()
        result.read(iprot)
        iprot.readMessageEnd()
        if result.success is not None:
            return result.success
        if result.ex is not None:
            raise result.ex
        raise TApplicationException(TApplicationException.MISSING_RESULT, "summarize failed: unknown result")

    def getCapabilities(self):
        self.send_getCapabilities()
        return self.recv_getCapabilities()

    def send_getCapabilities(self):
        self._oprot.writeMessageBegin('getCapabilities', TMessageType.CALL, self._seqid)
        args = getCapabilities_args()
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def recv_getCapabilities(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        result = getCapabilities_result()
        result.read(iprot)
        iprot.readMessageEnd()
        if result.success is not None:
            return result.success
        if result.ex is not None:
            raise result.ex
        raise TApplicationException(TApplicationException.MISSING_RESULT, "getCapabilities failed: unknown result")


class Processor(concrete.services.Service.Processor, Iface, TProcessor):
    def __init__(self, handler):
        concrete.services.Service.Processor.__init__(self, handler)
        self._processMap["summarize"] = Processor.process_summarize
        self._processMap["getCapabilities"] = Processor.process_getCapabilities
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

    def process_summarize(self, seqid, iprot, oprot):
        args = summarize_args()
        args.read(iprot)
        iprot.readMessageEnd()
        result = summarize_result()
        try:
            result.success = self._handler.summarize(args.query)
            msg_type = TMessageType.REPLY
        except TTransport.TTransportException:
            raise
        except concrete.services.ttypes.ServicesException as ex:
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
        oprot.writeMessageBegin("summarize", msg_type, seqid)
        result.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_getCapabilities(self, seqid, iprot, oprot):
        args = getCapabilities_args()
        args.read(iprot)
        iprot.readMessageEnd()
        result = getCapabilities_result()
        try:
            result.success = self._handler.getCapabilities()
            msg_type = TMessageType.REPLY
        except TTransport.TTransportException:
            raise
        except concrete.services.ttypes.ServicesException as ex:
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
        oprot.writeMessageBegin("getCapabilities", msg_type, seqid)
        result.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

# HELPER FUNCTIONS AND STRUCTURES


class summarize_args(object):
    """
    Attributes:
     - query

    """


    def __init__(self, query=None,):
        self.query = query

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
                    self.query = SummarizationRequest()
                    self.query.read(iprot)
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
        oprot.writeStructBegin('summarize_args')
        if self.query is not None:
            oprot.writeFieldBegin('query', TType.STRUCT, 1)
            self.query.write(oprot)
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
all_structs.append(summarize_args)
summarize_args.thrift_spec = (
    None,  # 0
    (1, TType.STRUCT, 'query', [SummarizationRequest, None], None, ),  # 1
)


class summarize_result(object):
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
                    self.success = Summary()
                    self.success.read(iprot)
                else:
                    iprot.skip(ftype)
            elif fid == 1:
                if ftype == TType.STRUCT:
                    self.ex = concrete.services.ttypes.ServicesException.read(iprot)
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
        oprot.writeStructBegin('summarize_result')
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
all_structs.append(summarize_result)
summarize_result.thrift_spec = (
    (0, TType.STRUCT, 'success', [Summary, None], None, ),  # 0
    (1, TType.STRUCT, 'ex', [concrete.services.ttypes.ServicesException, None], None, ),  # 1
)


class getCapabilities_args(object):


    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('getCapabilities_args')
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
all_structs.append(getCapabilities_args)
getCapabilities_args.thrift_spec = (
)


class getCapabilities_result(object):
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
                if ftype == TType.LIST:
                    self.success = []
                    (_etype24, _size21) = iprot.readListBegin()
                    for _i25 in range(_size21):
                        _elem26 = SummarizationCapability()
                        _elem26.read(iprot)
                        self.success.append(_elem26)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            elif fid == 1:
                if ftype == TType.STRUCT:
                    self.ex = concrete.services.ttypes.ServicesException.read(iprot)
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
        oprot.writeStructBegin('getCapabilities_result')
        if self.success is not None:
            oprot.writeFieldBegin('success', TType.LIST, 0)
            oprot.writeListBegin(TType.STRUCT, len(self.success))
            for iter27 in self.success:
                iter27.write(oprot)
            oprot.writeListEnd()
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
all_structs.append(getCapabilities_result)
getCapabilities_result.thrift_spec = (
    (0, TType.LIST, 'success', (TType.STRUCT, [SummarizationCapability, None], False), None, ),  # 0
    (1, TType.STRUCT, 'ex', [concrete.services.ttypes.ServicesException, None], None, ),  # 1
)
fix_spec(all_structs)
del all_structs
