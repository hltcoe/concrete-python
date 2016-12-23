"""Create a simple (valid) Communication suitable for testing purposes
"""

import time
import tempfile
import os
import logging

from concrete import (
    AnnotationMetadata,
    Communication,
    Section,
    Sentence,
    TextSpan,
    Token,
    Tokenization,
    TokenizationKind,
    TokenList
)
from concrete.util.concrete_uuid import AnalyticUUIDGeneratorFactory
from concrete.util.file_io import CommunicationWriter


AL_NONE = 'none'
AL_SECTION = 'section'
AL_SENTENCE = 'sentence'
AL_TOKEN = 'token'


def add_annotation_level_argparse_argument(parser):
    parser.add_argument('--annotation-level', type=str,
                        choices=(AL_NONE, AL_SECTION, AL_SENTENCE, AL_TOKEN),
                        help='Level of concrete annotation to infer from'
                             ' whitespace in text (%s: no annotation,'
                             ' %s: sections inferred'
                             ' from double-newline, %s: "%s" and sentences'
                             ' inferred from single-newline, %s: "%s" and'
                             ' tokens inferred from remaining whitespace)' %
                             (AL_NONE,
                              AL_SECTION,
                              AL_SENTENCE, AL_SECTION,
                              AL_TOKEN, AL_SENTENCE))


def _split(s, delim):
    pieces = s.split(delim)
    indexed_pieces = []
    offset = 0
    for p in pieces:
        indexed_pieces.append((p, offset, offset + len(p)))
        offset += len(p) + len(delim)
    return indexed_pieces


def create_sentence(sen_text, sen_start, sen_end,
                    aug, metadata_tool, metadata_timestamp,
                    annotation_level):
    '''
    Create sentence from provided text and metadata.
    Lower-level routine (called indirectly by create_comm).
    '''

    sections = (annotation_level is not None) and (annotation_level != AL_NONE)
    sentences = sections and (annotation_level != AL_SECTION)
    tokens = sentences and (annotation_level != AL_SENTENCE)

    return Sentence(
        uuid=aug.next(),
        textSpan=TextSpan(sen_start, sen_end),
        tokenization=Tokenization(
            uuid=aug.next(),
            kind=TokenizationKind.TOKEN_LIST,
            metadata=AnnotationMetadata(
                tool=metadata_tool,
                timestamp=metadata_timestamp,
            ),
            tokenList=TokenList(tokenList=[
                Token(
                    tokenIndex=i,
                    text=tok_text,
                )
                for (i, tok_text)
                in enumerate(sen_text.split())
            ]),
        ) if tokens else None,
    )


def create_section(sec_text, sec_start, sec_end, section_kind,
                   aug, metadata_tool, metadata_timestamp,
                   annotation_level):
    '''
    Create section from provided text and metadata.
    Lower-level routine (called by create_comm).
    '''

    sections = (annotation_level is not None) and (annotation_level != AL_NONE)
    sentences = sections and (annotation_level != AL_SECTION)

    return Section(
        uuid=aug.next(),
        textSpan=TextSpan(sec_start, sec_end),
        kind=section_kind,
        sentenceList=(
            [
                create_sentence(sen_text,
                                sec_start + sen_start,
                                sec_start + sen_end,
                                aug, metadata_tool, metadata_timestamp,
                                annotation_level)
                for (sen_text, sen_start, sen_end) in _split(sec_text, '\n')
            ] if ('\n' in sec_text) or sec_text.strip() else []
        ) if sentences else None,
    )


def create_comm(comm_id, text='',
                comm_type='article', section_kind='passage',
                metadata_tool='concrete-python',
                metadata_timestamp=None,
                annotation_level=AL_TOKEN):
    '''
    Create a simple, valid Communication from text.
    By default the text will be split by double-newlines into sections
    and then by single newlines into sentences within those sections.

    annotation_level controls the amount of annotation that is added:
      AL_NONE      add no optional annotations (not even sections)
      AL_SECTION   add sections but not sentences
      AL_SENTENCE  add sentences but not tokens
      AL_TOKEN     add all annotations, up to tokens (the default)

    If metadata_timestamp is None, the current time will be used.
    '''

    if metadata_timestamp is None:
        metadata_timestamp = int(time.time())

    augf = AnalyticUUIDGeneratorFactory()
    aug = augf.create()

    sections = (annotation_level is not None) and (annotation_level != AL_NONE)

    return Communication(
        id=comm_id,
        uuid=aug.next(),
        type=comm_type,
        text=text,
        metadata=AnnotationMetadata(
            tool=metadata_tool,
            timestamp=metadata_timestamp,
        ),
        sectionList=(
            [
                create_section(sec_text, sec_start, sec_end, section_kind,
                               aug, metadata_tool, metadata_timestamp,
                               annotation_level)
                for (sec_text, sec_start, sec_end) in _split(text, '\n\n')
            ] if text.strip() else []
        ) if sections else None,
    )


def create_simple_comm(comm_id, sentence_string="Super simple sentence ."):
    """Create a simple (valid) Communication suitable for testing purposes

    The Communication will have a single Section containing a single
    Sentence.

    Args:

    - `comm_id`: A string specifying a Communication ID
    - `sentence_string`: A string to be used for the sentence text.
       The string will be whitespace-tokenized.

    Returns:

    - A Concrete Communication object
    """
    logging.warning('create_simple_comm will be removed in a future'
                    ' release, please use create_comm instead')

    toolname = "TEST"
    timestamp = int(time.time())

    augf = AnalyticUUIDGeneratorFactory()
    aug = augf.create()

    comm = Communication(
        id=comm_id,
        metadata=AnnotationMetadata(tool=toolname, timestamp=timestamp),
        type=toolname,
        uuid=aug.next()
    )

    tokenization = Tokenization(
        kind=TokenizationKind.TOKEN_LIST,
        metadata=AnnotationMetadata(tool=toolname, timestamp=timestamp),
        tokenList=TokenList(
            tokenList=[]),
        uuid=aug.next()
    )
    token_string_list = sentence_string.split()
    for i, token_string in enumerate(token_string_list):
        tokenization.tokenList.tokenList.append(Token(text=token_string,
                                                      tokenIndex=i))

    sentence = Sentence(
        textSpan=TextSpan(0, len(sentence_string)),
        tokenization=tokenization,
        uuid=aug.next()
    )

    section = Section(
        kind="SectionKind",
        sentenceList=[sentence],
        textSpan=TextSpan(0, len(sentence_string)),
        uuid=aug.next()
    )

    comm.sectionList = [section]
    comm.text = sentence_string

    return comm


class SimpleCommTempFile(object):
    '''
    Class representing a temporary file of sample concrete objects.
    Designed to facilitate testing.  Class members:

        path:           path to file
        communications: list of communications that were written to file

    Usage demo:

    >>> from concrete.util import CommunicationReader
    >>> with SimpleCommTempFile(n=3, id_fmt='temp-%d') as f:
    ...     reader = CommunicationReader(f.path)
    ...     for (orig_comm, comm_path_pair) in zip(f.communications, reader):
    ...         print orig_comm.id
    ...         print orig_comm.id == comm_path_pair[0].id
    ...         print f.path == comm_path_pair[1]
    temp-0
    True
    True
    temp-1
    True
    True
    temp-2
    True
    True
    '''

    def __init__(self, n=10, id_fmt='temp-%d',
                 sentence_fmt='Super simple sentence %d .',
                 writer_class=CommunicationWriter, suffix='.concrete'):
        '''
        Create temp file and write communications.

            n:i     number of communications to write
            id_fmt: format string used to generate communication IDs;
                    should contain one instance of %d, which will be
                    replaced by the number of the communication
            sentence_fmt: format string used to generate communication
                    IDs; should contain one instance of %d, which will
                    be replaced by the number of the communication
            writer_class: CommunicationWriter or CommunicationTGZWriter
            suffix: file path suffix (you probably want to choose this
                    to match writer_class)
        '''
        logging.warning('SimpleCommTempFile will be removed in a future'
                        ' release, please use create_comm instead')

        (fd, path) = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        self.path = path
        self.communications = []
        w = writer_class()
        w.open(path)
        for i in xrange(n):
            comm = create_simple_comm(id_fmt % i, sentence_fmt % i)
            self.communications.append(comm)
            w.write(comm)
        w.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if os.path.exists(self.path):
            os.remove(self.path)
