"""
"""

import time

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


def create_simple_comm(comm_id, sentence_string="Super simple sentence ."):
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
