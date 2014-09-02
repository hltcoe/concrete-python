#
# Autogenerated by Thrift Compiler (1.0.0-dev)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py:new_style,utf8strings
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException
import concrete.structure.ttypes
import concrete.metadata.ttypes
import concrete.uuid.ttypes


from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None



class Entity(object):
  """
  A single referent (or "entity") that is referred to at least once
  in a given communication, along with pointers to all of the
  references to that referent. The referent's type (e.g., is it a
  person, or a location, or an organization, etc) is also recorded.

  Because each Entity contains pointers to all references to a
  referent with a given communication, an Entity can be
  thought of as a coreference set.

  Attributes:
   - uuid: Unique identifier for this entity.
   - mentionIdList: An list of pointers to all of the mentions of this Entity's
  referent.  (type=EntityMention)
   - type: The basic type of this entity's referent.
   - confidence: Confidence score for this individual entity.  You can also set a
  confidence score for an entire EntitySet using the EntitySet's
  metadata.
   - canonicalName: A string containing a representative, canonical, or "best" name
  for this entity's referent.  This string may match one of the
  mentions' text strings, but it is not required to.
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRUCT, 'uuid', (concrete.uuid.ttypes.UUID, concrete.uuid.ttypes.UUID.thrift_spec), None, ), # 1
    (2, TType.LIST, 'mentionIdList', (TType.STRUCT,(concrete.uuid.ttypes.UUID, concrete.uuid.ttypes.UUID.thrift_spec)), None, ), # 2
    (3, TType.STRING, 'type', None, None, ), # 3
    (4, TType.DOUBLE, 'confidence', None, None, ), # 4
    (5, TType.STRING, 'canonicalName', None, None, ), # 5
  )

  def __init__(self, uuid=None, mentionIdList=None, type=None, confidence=None, canonicalName=None,):
    self.uuid = uuid
    self.mentionIdList = mentionIdList
    self.type = type
    self.confidence = confidence
    self.canonicalName = canonicalName

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRUCT:
          self.uuid = concrete.uuid.ttypes.UUID()
          self.uuid.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.LIST:
          self.mentionIdList = []
          (_etype3, _size0) = iprot.readListBegin()
          for _i4 in xrange(_size0):
            _elem5 = concrete.uuid.ttypes.UUID()
            _elem5.read(iprot)
            self.mentionIdList.append(_elem5)
          iprot.readListEnd()
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.type = iprot.readString().decode('utf-8')
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.DOUBLE:
          self.confidence = iprot.readDouble();
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.STRING:
          self.canonicalName = iprot.readString().decode('utf-8')
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('Entity')
    if self.uuid is not None:
      oprot.writeFieldBegin('uuid', TType.STRUCT, 1)
      self.uuid.write(oprot)
      oprot.writeFieldEnd()
    if self.mentionIdList is not None:
      oprot.writeFieldBegin('mentionIdList', TType.LIST, 2)
      oprot.writeListBegin(TType.STRUCT, len(self.mentionIdList))
      for iter6 in self.mentionIdList:
        iter6.write(oprot)
      oprot.writeListEnd()
      oprot.writeFieldEnd()
    if self.type is not None:
      oprot.writeFieldBegin('type', TType.STRING, 3)
      oprot.writeString(self.type.encode('utf-8'))
      oprot.writeFieldEnd()
    if self.confidence is not None:
      oprot.writeFieldBegin('confidence', TType.DOUBLE, 4)
      oprot.writeDouble(self.confidence)
      oprot.writeFieldEnd()
    if self.canonicalName is not None:
      oprot.writeFieldBegin('canonicalName', TType.STRING, 5)
      oprot.writeString(self.canonicalName.encode('utf-8'))
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    if self.uuid is None:
      raise TProtocol.TProtocolException(message='Required field uuid is unset!')
    if self.mentionIdList is None:
      raise TProtocol.TProtocolException(message='Required field mentionIdList is unset!')
    if self.type is None:
      raise TProtocol.TProtocolException(message='Required field type is unset!')
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class EntitySet(object):
  """
  A theory about the set of entities that are present in a
  message. See also: Entity.

  Attributes:
   - uuid: Unique identifier for this set.
   - metadata: Information about where this set came from.
   - entityList: List of entities in this set.
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRUCT, 'uuid', (concrete.uuid.ttypes.UUID, concrete.uuid.ttypes.UUID.thrift_spec), None, ), # 1
    (2, TType.STRUCT, 'metadata', (concrete.metadata.ttypes.AnnotationMetadata, concrete.metadata.ttypes.AnnotationMetadata.thrift_spec), None, ), # 2
    (3, TType.LIST, 'entityList', (TType.STRUCT,(Entity, Entity.thrift_spec)), None, ), # 3
  )

  def __init__(self, uuid=None, metadata=None, entityList=None,):
    self.uuid = uuid
    self.metadata = metadata
    self.entityList = entityList

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRUCT:
          self.uuid = concrete.uuid.ttypes.UUID()
          self.uuid.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRUCT:
          self.metadata = concrete.metadata.ttypes.AnnotationMetadata()
          self.metadata.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.LIST:
          self.entityList = []
          (_etype10, _size7) = iprot.readListBegin()
          for _i11 in xrange(_size7):
            _elem12 = Entity()
            _elem12.read(iprot)
            self.entityList.append(_elem12)
          iprot.readListEnd()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('EntitySet')
    if self.uuid is not None:
      oprot.writeFieldBegin('uuid', TType.STRUCT, 1)
      self.uuid.write(oprot)
      oprot.writeFieldEnd()
    if self.metadata is not None:
      oprot.writeFieldBegin('metadata', TType.STRUCT, 2)
      self.metadata.write(oprot)
      oprot.writeFieldEnd()
    if self.entityList is not None:
      oprot.writeFieldBegin('entityList', TType.LIST, 3)
      oprot.writeListBegin(TType.STRUCT, len(self.entityList))
      for iter13 in self.entityList:
        iter13.write(oprot)
      oprot.writeListEnd()
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    if self.uuid is None:
      raise TProtocol.TProtocolException(message='Required field uuid is unset!')
    if self.entityList is None:
      raise TProtocol.TProtocolException(message='Required field entityList is unset!')
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class EntityMention(object):
  """
  A span of text with a specific referent, such as a person,
  organization, or time. Things that can be referred to by a mention
  are called "entities."

  It is left up to individual EntityMention taggers to decide which
  referent types and phrase types to identify. For example, some
  EntityMention taggers may only identify proper nouns, or may only
  identify EntityMentions that refer to people.

  Each EntityMention consists of a sequence of tokens. This sequence
  is usually annotated with information about the referent type
  (e.g., is it a person, or a location, or an organization, etc) as
  well as the phrase type (is it a name, pronoun, common noun, etc.).

  EntityMentions typically consist of a single noun phrase; however,
  other phrase types may also be marked as mentions. For
  example, in the phrase "French hotel," the adjective "French" might
  be marked as a mention for France.

  Attributes:
   - uuid
   - tokens: List of mentions in this set.
   - entityType: The type of referent that is referred to by this mention.
   - phraseType: The phrase type of the tokens that constitute this mention.
   - confidence: A confidence score for this individual mention.  You can also
  set a confidence score for an entire EntityMentionSet using the
  EntityMentionSet's metadata.
   - text: The text content of this entity mention.  This field is
  typically redundant with the 'token_sequence' field, and may not
  be generated by all analytics.
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRUCT, 'uuid', (concrete.uuid.ttypes.UUID, concrete.uuid.ttypes.UUID.thrift_spec), None, ), # 1
    (2, TType.STRUCT, 'tokens', (concrete.structure.ttypes.TokenRefSequence, concrete.structure.ttypes.TokenRefSequence.thrift_spec), None, ), # 2
    (3, TType.STRING, 'entityType', None, None, ), # 3
    (4, TType.STRING, 'phraseType', None, None, ), # 4
    (5, TType.DOUBLE, 'confidence', None, None, ), # 5
    (6, TType.STRING, 'text', None, None, ), # 6
  )

  def __init__(self, uuid=None, tokens=None, entityType=None, phraseType=None, confidence=None, text=None,):
    self.uuid = uuid
    self.tokens = tokens
    self.entityType = entityType
    self.phraseType = phraseType
    self.confidence = confidence
    self.text = text

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRUCT:
          self.uuid = concrete.uuid.ttypes.UUID()
          self.uuid.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRUCT:
          self.tokens = concrete.structure.ttypes.TokenRefSequence()
          self.tokens.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.entityType = iprot.readString().decode('utf-8')
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRING:
          self.phraseType = iprot.readString().decode('utf-8')
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.DOUBLE:
          self.confidence = iprot.readDouble();
        else:
          iprot.skip(ftype)
      elif fid == 6:
        if ftype == TType.STRING:
          self.text = iprot.readString().decode('utf-8')
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('EntityMention')
    if self.uuid is not None:
      oprot.writeFieldBegin('uuid', TType.STRUCT, 1)
      self.uuid.write(oprot)
      oprot.writeFieldEnd()
    if self.tokens is not None:
      oprot.writeFieldBegin('tokens', TType.STRUCT, 2)
      self.tokens.write(oprot)
      oprot.writeFieldEnd()
    if self.entityType is not None:
      oprot.writeFieldBegin('entityType', TType.STRING, 3)
      oprot.writeString(self.entityType.encode('utf-8'))
      oprot.writeFieldEnd()
    if self.phraseType is not None:
      oprot.writeFieldBegin('phraseType', TType.STRING, 4)
      oprot.writeString(self.phraseType.encode('utf-8'))
      oprot.writeFieldEnd()
    if self.confidence is not None:
      oprot.writeFieldBegin('confidence', TType.DOUBLE, 5)
      oprot.writeDouble(self.confidence)
      oprot.writeFieldEnd()
    if self.text is not None:
      oprot.writeFieldBegin('text', TType.STRING, 6)
      oprot.writeString(self.text.encode('utf-8'))
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    if self.uuid is None:
      raise TProtocol.TProtocolException(message='Required field uuid is unset!')
    if self.tokens is None:
      raise TProtocol.TProtocolException(message='Required field tokens is unset!')
    if self.entityType is None:
      raise TProtocol.TProtocolException(message='Required field entityType is unset!')
    if self.phraseType is None:
      raise TProtocol.TProtocolException(message='Required field phraseType is unset!')
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class EntityMentionSet(object):
  """
  A theory about the set of entity mentions that are present in a
  message. See also: EntityMention

  This type does not represent a coreference relationship, which is handled by Entity.
  This type is meant to represent the output of a entity-mention-identifier,
  which is often a part of an in-doc coreference system.

  Attributes:
   - uuid: Unique identifier for this set.
   - metadata: Information about where this set came from.
   - mentionList: List of mentions in this set.
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRUCT, 'uuid', (concrete.uuid.ttypes.UUID, concrete.uuid.ttypes.UUID.thrift_spec), None, ), # 1
    (2, TType.STRUCT, 'metadata', (concrete.metadata.ttypes.AnnotationMetadata, concrete.metadata.ttypes.AnnotationMetadata.thrift_spec), None, ), # 2
    (3, TType.LIST, 'mentionList', (TType.STRUCT,(EntityMention, EntityMention.thrift_spec)), None, ), # 3
  )

  def __init__(self, uuid=None, metadata=None, mentionList=None,):
    self.uuid = uuid
    self.metadata = metadata
    self.mentionList = mentionList

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRUCT:
          self.uuid = concrete.uuid.ttypes.UUID()
          self.uuid.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRUCT:
          self.metadata = concrete.metadata.ttypes.AnnotationMetadata()
          self.metadata.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.LIST:
          self.mentionList = []
          (_etype17, _size14) = iprot.readListBegin()
          for _i18 in xrange(_size14):
            _elem19 = EntityMention()
            _elem19.read(iprot)
            self.mentionList.append(_elem19)
          iprot.readListEnd()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('EntityMentionSet')
    if self.uuid is not None:
      oprot.writeFieldBegin('uuid', TType.STRUCT, 1)
      self.uuid.write(oprot)
      oprot.writeFieldEnd()
    if self.metadata is not None:
      oprot.writeFieldBegin('metadata', TType.STRUCT, 2)
      self.metadata.write(oprot)
      oprot.writeFieldEnd()
    if self.mentionList is not None:
      oprot.writeFieldBegin('mentionList', TType.LIST, 3)
      oprot.writeListBegin(TType.STRUCT, len(self.mentionList))
      for iter20 in self.mentionList:
        iter20.write(oprot)
      oprot.writeListEnd()
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    if self.uuid is None:
      raise TProtocol.TProtocolException(message='Required field uuid is unset!')
    if self.mentionList is None:
      raise TProtocol.TProtocolException(message='Required field mentionList is unset!')
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)
