"""Create a simple (valid) Communication suitable for testing purposes
"""

import time
import tempfile
import os

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
from concrete.util import generate_UUID
from concrete.util.file_io import CommunicationWriter


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
    toolname="TEST"
    timestamp = int(time.time())

    comm = Communication(
        id=comm_id,
        metadata=AnnotationMetadata(tool=toolname, timestamp=timestamp),
        type=toolname,
        uuid=generate_UUID())

    tokenization = Tokenization(
        kind=TokenizationKind.TOKEN_LIST,
        metadata=AnnotationMetadata(tool=toolname, timestamp=timestamp),
        tokenList=TokenList(
            tokenList=[]),
        uuid=generate_UUID())
    token_string_list = sentence_string.split()
    for i, token_string in enumerate(token_string_list):
        tokenization.tokenList.tokenList.append(Token(text=token_string, tokenIndex=i))

    sentence = Sentence(
        textSpan=TextSpan(0, len(sentence_string)),
        tokenization=tokenization,
        uuid=generate_UUID())

    section = Section(
        kind="SectionKind",
        sentenceList=[sentence],
        textSpan=TextSpan(0, len(sentence_string)),
        uuid=generate_UUID())

    comm.sectionList=[section]

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
