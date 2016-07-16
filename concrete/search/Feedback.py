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
import logging
from .ttypes import *
from thrift.Thrift import TProcessor
from thrift.transport import TTransport


class Iface(object):
    def startFeedback(self, results):
        """
        Start providing feedback for the specified SearchResults.
        This causes the search and its results to be persisted.

        Parameters:
         - results
        """
        pass

    def addCommunicationFeedback(self, searchResultsId, communicationId, feedback):
        """
        Provide feedback on the relevance of a particular communication to a search

        Parameters:
         - searchResultsId
         - communicationId
         - feedback
        """
        pass

    def addSentenceFeedback(self, searchResultsId, communicationId, sentenceId, feedback):
        """
        Provide feedback on the relevance of a particular sentence to a search

        Parameters:
         - searchResultsId
         - communicationId
         - sentenceId
         - feedback
        """
        pass


class Client(Iface):
    def __init__(self, iprot, oprot=None):
        self._iprot = self._oprot = iprot
        if oprot is not None:
            self._oprot = oprot
        self._seqid = 0

    def startFeedback(self, results):
        """
        Start providing feedback for the specified SearchResults.
        This causes the search and its results to be persisted.

        Parameters:
         - results
        """
        self.send_startFeedback(results)
        self.recv_startFeedback()

    def send_startFeedback(self, results):
        self._oprot.writeMessageBegin('startFeedback', TMessageType.CALL, self._seqid)
        args = startFeedback_args()
        args.results = results
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def recv_startFeedback(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        result = startFeedback_result()
        result.read(iprot)
        iprot.readMessageEnd()
        return

    def addCommunicationFeedback(self, searchResultsId, communicationId, feedback):
        """
        Provide feedback on the relevance of a particular communication to a search

        Parameters:
         - searchResultsId
         - communicationId
         - feedback
        """
        self.send_addCommunicationFeedback(searchResultsId, communicationId, feedback)
        self.recv_addCommunicationFeedback()

    def send_addCommunicationFeedback(self, searchResultsId, communicationId, feedback):
        self._oprot.writeMessageBegin('addCommunicationFeedback', TMessageType.CALL, self._seqid)
        args = addCommunicationFeedback_args()
        args.searchResultsId = searchResultsId
        args.communicationId = communicationId
        args.feedback = feedback
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def recv_addCommunicationFeedback(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        result = addCommunicationFeedback_result()
        result.read(iprot)
        iprot.readMessageEnd()
        return

    def addSentenceFeedback(self, searchResultsId, communicationId, sentenceId, feedback):
        """
        Provide feedback on the relevance of a particular sentence to a search

        Parameters:
         - searchResultsId
         - communicationId
         - sentenceId
         - feedback
        """
        self.send_addSentenceFeedback(searchResultsId, communicationId, sentenceId, feedback)
        self.recv_addSentenceFeedback()

    def send_addSentenceFeedback(self, searchResultsId, communicationId, sentenceId, feedback):
        self._oprot.writeMessageBegin('addSentenceFeedback', TMessageType.CALL, self._seqid)
        args = addSentenceFeedback_args()
        args.searchResultsId = searchResultsId
        args.communicationId = communicationId
        args.sentenceId = sentenceId
        args.feedback = feedback
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def recv_addSentenceFeedback(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        result = addSentenceFeedback_result()
        result.read(iprot)
        iprot.readMessageEnd()
        return


class Processor(Iface, TProcessor):
    def __init__(self, handler):
        self._handler = handler
        self._processMap = {}
        self._processMap["startFeedback"] = Processor.process_startFeedback
        self._processMap["addCommunicationFeedback"] = Processor.process_addCommunicationFeedback
        self._processMap["addSentenceFeedback"] = Processor.process_addSentenceFeedback

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

    def process_startFeedback(self, seqid, iprot, oprot):
        args = startFeedback_args()
        args.read(iprot)
        iprot.readMessageEnd()
        result = startFeedback_result()
        try:
            self._handler.startFeedback(args.results)
            msg_type = TMessageType.REPLY
        except (TTransport.TTransportException, KeyboardInterrupt, SystemExit):
            raise
        except Exception as ex:
            msg_type = TMessageType.EXCEPTION
            logging.exception(ex)
            result = TApplicationException(TApplicationException.INTERNAL_ERROR, 'Internal error')
        oprot.writeMessageBegin("startFeedback", msg_type, seqid)
        result.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_addCommunicationFeedback(self, seqid, iprot, oprot):
        args = addCommunicationFeedback_args()
        args.read(iprot)
        iprot.readMessageEnd()
        result = addCommunicationFeedback_result()
        try:
            self._handler.addCommunicationFeedback(args.searchResultsId, args.communicationId, args.feedback)
            msg_type = TMessageType.REPLY
        except (TTransport.TTransportException, KeyboardInterrupt, SystemExit):
            raise
        except Exception as ex:
            msg_type = TMessageType.EXCEPTION
            logging.exception(ex)
            result = TApplicationException(TApplicationException.INTERNAL_ERROR, 'Internal error')
        oprot.writeMessageBegin("addCommunicationFeedback", msg_type, seqid)
        result.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_addSentenceFeedback(self, seqid, iprot, oprot):
        args = addSentenceFeedback_args()
        args.read(iprot)
        iprot.readMessageEnd()
        result = addSentenceFeedback_result()
        try:
            self._handler.addSentenceFeedback(args.searchResultsId, args.communicationId, args.sentenceId, args.feedback)
            msg_type = TMessageType.REPLY
        except (TTransport.TTransportException, KeyboardInterrupt, SystemExit):
            raise
        except Exception as ex:
            msg_type = TMessageType.EXCEPTION
            logging.exception(ex)
            result = TApplicationException(TApplicationException.INTERNAL_ERROR, 'Internal error')
        oprot.writeMessageBegin("addSentenceFeedback", msg_type, seqid)
        result.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

# HELPER FUNCTIONS AND STRUCTURES


class startFeedback_args(object):
    """
    Attributes:
     - results
    """

    thrift_spec = (
        None,  # 0
        (1, TType.STRUCT, 'results', (SearchResults, SearchResults.thrift_spec), None, ),  # 1
    )

    def __init__(self, results=None,):
        self.results = results

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
                    self.results = SearchResults()
                    self.results.read(iprot)
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
        oprot.writeStructBegin('startFeedback_args')
        if self.results is not None:
            oprot.writeFieldBegin('results', TType.STRUCT, 1)
            self.results.write(oprot)
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


class startFeedback_result(object):

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
        oprot.writeStructBegin('startFeedback_result')
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


class addCommunicationFeedback_args(object):
    """
    Attributes:
     - searchResultsId
     - communicationId
     - feedback
    """

    thrift_spec = (
        None,  # 0
        (1, TType.STRUCT, 'searchResultsId', (concrete.uuid.ttypes.UUID, concrete.uuid.ttypes.UUID.thrift_spec), None, ),  # 1
        (2, TType.STRING, 'communicationId', 'UTF8', None, ),  # 2
        (3, TType.I32, 'feedback', None, None, ),  # 3
    )

    def __init__(self, searchResultsId=None, communicationId=None, feedback=None,):
        self.searchResultsId = searchResultsId
        self.communicationId = communicationId
        self.feedback = feedback

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
                    self.searchResultsId = concrete.uuid.ttypes.UUID()
                    self.searchResultsId.read(iprot)
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.STRING:
                    self.communicationId = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.I32:
                    self.feedback = iprot.readI32()
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
        oprot.writeStructBegin('addCommunicationFeedback_args')
        if self.searchResultsId is not None:
            oprot.writeFieldBegin('searchResultsId', TType.STRUCT, 1)
            self.searchResultsId.write(oprot)
            oprot.writeFieldEnd()
        if self.communicationId is not None:
            oprot.writeFieldBegin('communicationId', TType.STRING, 2)
            oprot.writeString(self.communicationId.encode('utf-8') if sys.version_info[0] == 2 else self.communicationId)
            oprot.writeFieldEnd()
        if self.feedback is not None:
            oprot.writeFieldBegin('feedback', TType.I32, 3)
            oprot.writeI32(self.feedback)
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


class addCommunicationFeedback_result(object):

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
        oprot.writeStructBegin('addCommunicationFeedback_result')
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


class addSentenceFeedback_args(object):
    """
    Attributes:
     - searchResultsId
     - communicationId
     - sentenceId
     - feedback
    """

    thrift_spec = (
        None,  # 0
        (1, TType.STRUCT, 'searchResultsId', (concrete.uuid.ttypes.UUID, concrete.uuid.ttypes.UUID.thrift_spec), None, ),  # 1
        (2, TType.STRING, 'communicationId', 'UTF8', None, ),  # 2
        (3, TType.STRUCT, 'sentenceId', (concrete.uuid.ttypes.UUID, concrete.uuid.ttypes.UUID.thrift_spec), None, ),  # 3
        (4, TType.I32, 'feedback', None, None, ),  # 4
    )

    def __init__(self, searchResultsId=None, communicationId=None, sentenceId=None, feedback=None,):
        self.searchResultsId = searchResultsId
        self.communicationId = communicationId
        self.sentenceId = sentenceId
        self.feedback = feedback

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
                    self.searchResultsId = concrete.uuid.ttypes.UUID()
                    self.searchResultsId.read(iprot)
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.STRING:
                    self.communicationId = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.STRUCT:
                    self.sentenceId = concrete.uuid.ttypes.UUID()
                    self.sentenceId.read(iprot)
                else:
                    iprot.skip(ftype)
            elif fid == 4:
                if ftype == TType.I32:
                    self.feedback = iprot.readI32()
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
        oprot.writeStructBegin('addSentenceFeedback_args')
        if self.searchResultsId is not None:
            oprot.writeFieldBegin('searchResultsId', TType.STRUCT, 1)
            self.searchResultsId.write(oprot)
            oprot.writeFieldEnd()
        if self.communicationId is not None:
            oprot.writeFieldBegin('communicationId', TType.STRING, 2)
            oprot.writeString(self.communicationId.encode('utf-8') if sys.version_info[0] == 2 else self.communicationId)
            oprot.writeFieldEnd()
        if self.sentenceId is not None:
            oprot.writeFieldBegin('sentenceId', TType.STRUCT, 3)
            self.sentenceId.write(oprot)
            oprot.writeFieldEnd()
        if self.feedback is not None:
            oprot.writeFieldBegin('feedback', TType.I32, 4)
            oprot.writeI32(self.feedback)
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


class addSentenceFeedback_result(object):

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
        oprot.writeStructBegin('addSentenceFeedback_result')
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