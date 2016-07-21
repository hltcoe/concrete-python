# -*- coding: utf-8 -*-
#
# Autogenerated by Thrift Compiler (1.0.0-dev)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py:coding=utf-8
#

from thrift.Thrift import TType, TMessageType, TFrozenDict, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
import sys
import concrete.services.Service
import logging
from .ttypes import *
from thrift.Thrift import TProcessor
from thrift.transport import TTransport


class Iface(concrete.services.Service.Iface):
    """
    The active learning server is responsible for sorting a list of communications.
    Users annotate communications based on the sort.

    Active learning is an asynchronous process.
    It is started by the client calling start().
    At arbitrary times, the client can call addAnnotations().
    When the server is done with a sort of the data, it calls submitSort() on the client.
    The server can perform additional sorts until stop() is called.

    The server must be preconfigured with the details of the data source to pull communications.
    """
    def start(self, sessionId, task, contact):
        """
        Start an active learning session on these communications

        Parameters:
         - sessionId
         - task
         - contact
        """
        pass

    def stop(self, sessionId):
        """
        Stop the learning session

        Parameters:
         - sessionId
        """
        pass

    def addAnnotations(self, sessionId, annotations):
        """
        Add annotations from the user to the learning process

        Parameters:
         - sessionId
         - annotations
        """
        pass


class Client(concrete.services.Service.Client, Iface):
    """
    The active learning server is responsible for sorting a list of communications.
    Users annotate communications based on the sort.

    Active learning is an asynchronous process.
    It is started by the client calling start().
    At arbitrary times, the client can call addAnnotations().
    When the server is done with a sort of the data, it calls submitSort() on the client.
    The server can perform additional sorts until stop() is called.

    The server must be preconfigured with the details of the data source to pull communications.
    """
    def __init__(self, iprot, oprot=None):
        concrete.services.Service.Client.__init__(self, iprot, oprot)

    def start(self, sessionId, task, contact):
        """
        Start an active learning session on these communications

        Parameters:
         - sessionId
         - task
         - contact
        """
        self.send_start(sessionId, task, contact)
        return self.recv_start()

    def send_start(self, sessionId, task, contact):
        self._oprot.writeMessageBegin('start', TMessageType.CALL, self._seqid)
        args = start_args()
        args.sessionId = sessionId
        args.task = task
        args.contact = contact
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def recv_start(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        result = start_result()
        result.read(iprot)
        iprot.readMessageEnd()
        if result.success is not None:
            return result.success
        raise TApplicationException(TApplicationException.MISSING_RESULT, "start failed: unknown result")

    def stop(self, sessionId):
        """
        Stop the learning session

        Parameters:
         - sessionId
        """
        self.send_stop(sessionId)
        self.recv_stop()

    def send_stop(self, sessionId):
        self._oprot.writeMessageBegin('stop', TMessageType.CALL, self._seqid)
        args = stop_args()
        args.sessionId = sessionId
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def recv_stop(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        result = stop_result()
        result.read(iprot)
        iprot.readMessageEnd()
        return

    def addAnnotations(self, sessionId, annotations):
        """
        Add annotations from the user to the learning process

        Parameters:
         - sessionId
         - annotations
        """
        self.send_addAnnotations(sessionId, annotations)
        self.recv_addAnnotations()

    def send_addAnnotations(self, sessionId, annotations):
        self._oprot.writeMessageBegin('addAnnotations', TMessageType.CALL, self._seqid)
        args = addAnnotations_args()
        args.sessionId = sessionId
        args.annotations = annotations
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def recv_addAnnotations(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        result = addAnnotations_result()
        result.read(iprot)
        iprot.readMessageEnd()
        return


class Processor(concrete.services.Service.Processor, Iface, TProcessor):
    def __init__(self, handler):
        concrete.services.Service.Processor.__init__(self, handler)
        self._processMap["start"] = Processor.process_start
        self._processMap["stop"] = Processor.process_stop
        self._processMap["addAnnotations"] = Processor.process_addAnnotations

    def process(self, iprot, oprot):
        (name, type, seqid) = iprot.readMessageBegin()
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

    def process_start(self, seqid, iprot, oprot):
        args = start_args()
        args.read(iprot)
        iprot.readMessageEnd()
        result = start_result()
        try:
            result.success = self._handler.start(args.sessionId, args.task, args.contact)
            msg_type = TMessageType.REPLY
        except (TTransport.TTransportException, KeyboardInterrupt, SystemExit):
            raise
        except Exception as ex:
            msg_type = TMessageType.EXCEPTION
            logging.exception(ex)
            result = TApplicationException(TApplicationException.INTERNAL_ERROR, 'Internal error')
        oprot.writeMessageBegin("start", msg_type, seqid)
        result.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_stop(self, seqid, iprot, oprot):
        args = stop_args()
        args.read(iprot)
        iprot.readMessageEnd()
        result = stop_result()
        try:
            self._handler.stop(args.sessionId)
            msg_type = TMessageType.REPLY
        except (TTransport.TTransportException, KeyboardInterrupt, SystemExit):
            raise
        except Exception as ex:
            msg_type = TMessageType.EXCEPTION
            logging.exception(ex)
            result = TApplicationException(TApplicationException.INTERNAL_ERROR, 'Internal error')
        oprot.writeMessageBegin("stop", msg_type, seqid)
        result.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_addAnnotations(self, seqid, iprot, oprot):
        args = addAnnotations_args()
        args.read(iprot)
        iprot.readMessageEnd()
        result = addAnnotations_result()
        try:
            self._handler.addAnnotations(args.sessionId, args.annotations)
            msg_type = TMessageType.REPLY
        except (TTransport.TTransportException, KeyboardInterrupt, SystemExit):
            raise
        except Exception as ex:
            msg_type = TMessageType.EXCEPTION
            logging.exception(ex)
            result = TApplicationException(TApplicationException.INTERNAL_ERROR, 'Internal error')
        oprot.writeMessageBegin("addAnnotations", msg_type, seqid)
        result.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

# HELPER FUNCTIONS AND STRUCTURES


class start_args(object):
    """
    Attributes:
     - sessionId
     - task
     - contact
    """

    thrift_spec = (
        None,  # 0
        (1, TType.STRUCT, 'sessionId', (concrete.uuid.ttypes.UUID, concrete.uuid.ttypes.UUID.thrift_spec), None, ),  # 1
        (2, TType.STRUCT, 'task', (AnnotationTask, AnnotationTask.thrift_spec), None, ),  # 2
        (3, TType.STRUCT, 'contact', (concrete.services.ttypes.AsyncContactInfo, concrete.services.ttypes.AsyncContactInfo.thrift_spec), None, ),  # 3
    )

    def __init__(self, sessionId=None, task=None, contact=None,):
        self.sessionId = sessionId
        self.task = task
        self.contact = contact

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, (self.__class__, self.thrift_spec))
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRUCT:
                    self.sessionId = concrete.uuid.ttypes.UUID()
                    self.sessionId.read(iprot)
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.STRUCT:
                    self.task = AnnotationTask()
                    self.task.read(iprot)
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.STRUCT:
                    self.contact = concrete.services.ttypes.AsyncContactInfo()
                    self.contact.read(iprot)
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, (self.__class__, self.thrift_spec)))
            return
        oprot.writeStructBegin('start_args')
        if self.sessionId is not None:
            oprot.writeFieldBegin('sessionId', TType.STRUCT, 1)
            self.sessionId.write(oprot)
            oprot.writeFieldEnd()
        if self.task is not None:
            oprot.writeFieldBegin('task', TType.STRUCT, 2)
            self.task.write(oprot)
            oprot.writeFieldEnd()
        if self.contact is not None:
            oprot.writeFieldBegin('contact', TType.STRUCT, 3)
            self.contact.write(oprot)
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


class start_result(object):
    """
    Attributes:
     - success
    """

    thrift_spec = (
        (0, TType.BOOL, 'success', None, None, ),  # 0
    )

    def __init__(self, success=None,):
        self.success = success

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, (self.__class__, self.thrift_spec))
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 0:
                if ftype == TType.BOOL:
                    self.success = iprot.readBool()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, (self.__class__, self.thrift_spec)))
            return
        oprot.writeStructBegin('start_result')
        if self.success is not None:
            oprot.writeFieldBegin('success', TType.BOOL, 0)
            oprot.writeBool(self.success)
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


class stop_args(object):
    """
    Attributes:
     - sessionId
    """

    thrift_spec = (
        None,  # 0
        (1, TType.STRUCT, 'sessionId', (concrete.uuid.ttypes.UUID, concrete.uuid.ttypes.UUID.thrift_spec), None, ),  # 1
    )

    def __init__(self, sessionId=None,):
        self.sessionId = sessionId

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, (self.__class__, self.thrift_spec))
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRUCT:
                    self.sessionId = concrete.uuid.ttypes.UUID()
                    self.sessionId.read(iprot)
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, (self.__class__, self.thrift_spec)))
            return
        oprot.writeStructBegin('stop_args')
        if self.sessionId is not None:
            oprot.writeFieldBegin('sessionId', TType.STRUCT, 1)
            self.sessionId.write(oprot)
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


class stop_result(object):

    thrift_spec = (
    )

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, (self.__class__, self.thrift_spec))
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
            oprot.trans.write(oprot._fast_encode(self, (self.__class__, self.thrift_spec)))
            return
        oprot.writeStructBegin('stop_result')
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


class addAnnotations_args(object):
    """
    Attributes:
     - sessionId
     - annotations
    """

    thrift_spec = (
        None,  # 0
        (1, TType.STRUCT, 'sessionId', (concrete.uuid.ttypes.UUID, concrete.uuid.ttypes.UUID.thrift_spec), None, ),  # 1
        (2, TType.LIST, 'annotations', (TType.STRUCT, (Annotation, Annotation.thrift_spec), False), None, ),  # 2
    )

    def __init__(self, sessionId=None, annotations=None,):
        self.sessionId = sessionId
        self.annotations = annotations

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, (self.__class__, self.thrift_spec))
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRUCT:
                    self.sessionId = concrete.uuid.ttypes.UUID()
                    self.sessionId.read(iprot)
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.LIST:
                    self.annotations = []
                    (_etype10, _size7) = iprot.readListBegin()
                    for _i11 in range(_size7):
                        _elem12 = Annotation()
                        _elem12.read(iprot)
                        self.annotations.append(_elem12)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, (self.__class__, self.thrift_spec)))
            return
        oprot.writeStructBegin('addAnnotations_args')
        if self.sessionId is not None:
            oprot.writeFieldBegin('sessionId', TType.STRUCT, 1)
            self.sessionId.write(oprot)
            oprot.writeFieldEnd()
        if self.annotations is not None:
            oprot.writeFieldBegin('annotations', TType.LIST, 2)
            oprot.writeListBegin(TType.STRUCT, len(self.annotations))
            for iter13 in self.annotations:
                iter13.write(oprot)
            oprot.writeListEnd()
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


class addAnnotations_result(object):

    thrift_spec = (
    )

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, (self.__class__, self.thrift_spec))
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
            oprot.trans.write(oprot._fast_encode(self, (self.__class__, self.thrift_spec)))
            return
        oprot.writeStructBegin('addAnnotations_result')
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
