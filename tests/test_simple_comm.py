# vim: set fileencoding=utf-8 :

from concrete.validate import validate_communication

from concrete.util.simple_comm import (
    create_comm, create_simple_comm,
    AL_NONE, AL_SECTION, AL_SENTENCE
)


def test_create_simple_comm():
    comm = create_simple_comm('one')
    assert 'one' == comm.id
    assert 'Super simple sentence .' == comm.text
    assert validate_communication(comm)


def test_create_comm_empty():
    comm = create_comm('one')
    assert 'one' == comm.id
    assert '' == comm.text
    assert [] == comm.sectionList
    assert validate_communication(comm)


def test_create_comm_ws():
    comm = create_comm('one', '\t \t\r\n\n')
    assert 'one' == comm.id
    assert '\t \t\r\n\n' == comm.text
    assert [] == comm.sectionList
    assert validate_communication(comm)


def test_create_comm_unicode():
    comm = create_comm('one', u'狐狸\t\t.')
    assert 'one' == comm.id
    assert u'狐狸\t\t.' == comm.text
    assert 1 == len(comm.sectionList)
    sect = comm.sectionList[0]
    assert 0 == sect.textSpan.start
    assert 5 == sect.textSpan.ending
    assert 1 == len(sect.sentenceList)
    sent = sect.sentenceList[0]
    assert 0 == sent.textSpan.start
    assert 5 == sent.textSpan.ending
    tl = sent.tokenization.tokenList.tokenList
    assert 2 == len(tl)
    assert 0 == tl[0].tokenIndex
    assert u'狐狸' == tl[0].text
    assert 1 == tl[1].tokenIndex
    assert '.' == tl[1].text
    assert validate_communication(comm)


def test_create_comm_one_sentence():
    comm = create_comm('one', 'simple comm\t\t.')
    assert 'one' == comm.id
    assert 'simple comm\t\t.' == comm.text
    assert 1 == len(comm.sectionList)
    sect = comm.sectionList[0]
    assert 0 == sect.textSpan.start
    assert 14 == sect.textSpan.ending
    assert 1 == len(sect.sentenceList)
    sent = sect.sentenceList[0]
    assert 0 == sent.textSpan.start
    assert 14 == sent.textSpan.ending
    tl = sent.tokenization.tokenList.tokenList
    assert 3 == len(tl)
    assert 0 == tl[0].tokenIndex
    assert 'simple' == tl[0].text
    assert 1 == tl[1].tokenIndex
    assert 'comm' == tl[1].text
    assert 2 == tl[2].tokenIndex
    assert '.' == tl[2].text
    assert validate_communication(comm)


def test_create_comm_complex():
    comm = create_comm('one', '\n\nsimple comm\t\t.\nor ...\n\nisit?\n')
    assert 'one' == comm.id
    assert '\n\nsimple comm\t\t.\nor ...\n\nisit?\n' == comm.text
    assert 3 == len(comm.sectionList)

    sect = comm.sectionList[0]
    assert 0 == sect.textSpan.start
    assert 0 == sect.textSpan.ending
    assert 0 == len(sect.sentenceList)

    sect = comm.sectionList[1]
    assert 2 == sect.textSpan.start
    assert 23 == sect.textSpan.ending
    assert 2 == len(sect.sentenceList)
    sent = sect.sentenceList[0]
    assert 2 == sent.textSpan.start
    assert 16 == sent.textSpan.ending
    tl = sent.tokenization.tokenList.tokenList
    assert 3 == len(tl)
    assert 0 == tl[0].tokenIndex
    assert 'simple' == tl[0].text
    assert 1 == tl[1].tokenIndex
    assert 'comm' == tl[1].text
    assert 2 == tl[2].tokenIndex
    assert '.' == tl[2].text
    sent = sect.sentenceList[1]
    assert 17 == sent.textSpan.start
    assert 23 == sent.textSpan.ending
    tl = sent.tokenization.tokenList.tokenList
    assert 2 == len(tl)
    assert 0 == tl[0].tokenIndex
    assert 'or' == tl[0].text
    assert 1 == tl[1].tokenIndex
    assert '...' == tl[1].text

    sect = comm.sectionList[2]
    assert 25 == sect.textSpan.start
    assert 31 == sect.textSpan.ending
    assert 2 == len(sect.sentenceList)
    sent = sect.sentenceList[0]
    assert 25 == sent.textSpan.start
    assert 30 == sent.textSpan.ending
    tl = sent.tokenization.tokenList.tokenList
    assert 1 == len(tl)
    assert 0 == tl[0].tokenIndex
    assert 'isit?' == tl[0].text
    sent = sect.sentenceList[1]
    assert 31 == sent.textSpan.start
    assert 31 == sent.textSpan.ending
    tl = sent.tokenization.tokenList.tokenList
    assert 0 == len(tl)

    assert validate_communication(comm)


def test_create_comm_empty_al_none():
    comm = create_comm('one', annotation_level=AL_NONE)
    assert 'one' == comm.id
    assert '' == comm.text
    assert comm.sectionList is None
    assert validate_communication(comm)


def test_create_comm_ws_al_none():
    comm = create_comm('one', '\t \t\r\n\n', annotation_level=AL_NONE)
    assert 'one' == comm.id
    assert '\t \t\r\n\n' == comm.text
    assert comm.sectionList is None
    assert validate_communication(comm)


def test_create_comm_unicode_al_none():
    comm = create_comm('one', u'狐狸\t\t.', annotation_level=AL_NONE)
    assert 'one' == comm.id
    assert u'狐狸\t\t.' == comm.text
    assert comm.sectionList is None
    assert validate_communication(comm)


def test_create_comm_one_sentence_al_none():
    comm = create_comm('one', 'simple comm\t\t.', annotation_level=AL_NONE)
    assert 'one' == comm.id
    assert 'simple comm\t\t.' == comm.text
    assert comm.sectionList is None
    assert validate_communication(comm)


def test_create_comm_complex_al_none():
    comm = create_comm('one', '\n\nsimple comm\t\t.\nor ...\n\nisit?\n',
                       annotation_level=AL_NONE)
    assert 'one' == comm.id
    assert '\n\nsimple comm\t\t.\nor ...\n\nisit?\n' == comm.text
    assert comm.sectionList is None
    assert validate_communication(comm)


def test_create_comm_empty_al_section():
    comm = create_comm('one', annotation_level=AL_SECTION)
    assert 'one' == comm.id
    assert '' == comm.text
    assert [] == comm.sectionList
    assert validate_communication(comm)


def test_create_comm_ws_al_section():
    comm = create_comm('one', '\t \t\r\n\n', annotation_level=AL_SECTION)
    assert 'one' == comm.id
    assert '\t \t\r\n\n' == comm.text
    assert [] == comm.sectionList
    assert validate_communication(comm)


def test_create_comm_unicode_al_section():
    comm = create_comm('one', u'狐狸\t\t.', annotation_level=AL_SECTION)
    assert 'one' == comm.id
    assert u'狐狸\t\t.' == comm.text
    assert 1 == len(comm.sectionList)
    sect = comm.sectionList[0]
    assert 0 == sect.textSpan.start
    assert 5 == sect.textSpan.ending
    assert sect.sentenceList is None
    assert validate_communication(comm)


def test_create_comm_one_sentence_al_section():
    comm = create_comm('one', 'simple comm\t\t.', annotation_level=AL_SECTION)
    assert 'one' == comm.id
    assert 'simple comm\t\t.' == comm.text
    assert 1 == len(comm.sectionList)
    sect = comm.sectionList[0]
    assert 0 == sect.textSpan.start
    assert 14 == sect.textSpan.ending
    assert sect.sentenceList is None
    assert validate_communication(comm)


def test_create_comm_complex_al_section():
    comm = create_comm('one', '\n\nsimple comm\t\t.\nor ...\n\nisit?\n',
                       annotation_level=AL_SECTION)
    assert 'one' == comm.id
    assert '\n\nsimple comm\t\t.\nor ...\n\nisit?\n' == comm.text

    assert 3 == len(comm.sectionList)

    sect = comm.sectionList[0]
    assert 0 == sect.textSpan.start
    assert 0 == sect.textSpan.ending
    assert sect.sentenceList is None

    sect = comm.sectionList[1]
    assert 2 == sect.textSpan.start
    assert 23 == sect.textSpan.ending
    assert sect.sentenceList is None

    sect = comm.sectionList[2]
    assert 25 == sect.textSpan.start
    assert 31 == sect.textSpan.ending
    assert sect.sentenceList is None

    assert validate_communication(comm)


def test_create_comm_empty_al_sentence():
    comm = create_comm('one', annotation_level=AL_SENTENCE)
    assert 'one' == comm.id
    assert '' == comm.text
    assert [] == comm.sectionList
    assert validate_communication(comm)


def test_create_comm_ws_al_sentence():
    comm = create_comm('one', '\t \t\r\n\n', annotation_level=AL_SENTENCE)
    assert 'one' == comm.id
    assert '\t \t\r\n\n' == comm.text
    assert [] == comm.sectionList
    assert validate_communication(comm)


def test_create_comm_unicode_al_sentence():
    comm = create_comm('one', u'狐狸\t\t.', annotation_level=AL_SENTENCE)
    assert 'one' == comm.id
    assert u'狐狸\t\t.' == comm.text
    assert 1 == len(comm.sectionList)
    sect = comm.sectionList[0]
    assert 0 == sect.textSpan.start
    assert 5 == sect.textSpan.ending
    assert 1 == len(sect.sentenceList)
    sent = sect.sentenceList[0]
    assert 0 == sent.textSpan.start
    assert 5 == sent.textSpan.ending
    assert sent.tokenization is None
    assert validate_communication(comm)


def test_create_comm_one_sentence_al_sentence():
    comm = create_comm('one', 'simple comm\t\t.', annotation_level=AL_SENTENCE)
    assert 'one' == comm.id
    assert 'simple comm\t\t.' == comm.text
    assert 1 == len(comm.sectionList)
    sect = comm.sectionList[0]
    assert 0 == sect.textSpan.start
    assert 14 == sect.textSpan.ending
    assert 1 == len(sect.sentenceList)
    sent = sect.sentenceList[0]
    assert 0 == sent.textSpan.start
    assert 14 == sent.textSpan.ending
    assert sent.tokenization is None
    assert validate_communication(comm)


def test_create_comm_complex_al_sentence():
    comm = create_comm('one', '\n\nsimple comm\t\t.\nor ...\n\nisit?\n',
                       annotation_level=AL_SENTENCE)
    assert 'one' == comm.id
    assert '\n\nsimple comm\t\t.\nor ...\n\nisit?\n' == comm.text
    assert 3 == len(comm.sectionList)

    sect = comm.sectionList[0]
    assert 0 == sect.textSpan.start
    assert 0 == sect.textSpan.ending
    assert 0 == len(sect.sentenceList)

    sect = comm.sectionList[1]
    assert 2 == sect.textSpan.start
    assert 23 == sect.textSpan.ending
    assert 2 == len(sect.sentenceList)
    sent = sect.sentenceList[0]
    assert 2 == sent.textSpan.start
    assert 16 == sent.textSpan.ending
    assert sent.tokenization is None
    sent = sect.sentenceList[1]
    assert 17 == sent.textSpan.start
    assert 23 == sent.textSpan.ending
    assert sent.tokenization is None

    sect = comm.sectionList[2]
    assert 25 == sect.textSpan.start
    assert 31 == sect.textSpan.ending
    assert 2 == len(sect.sentenceList)
    sent = sect.sentenceList[0]
    assert 25 == sent.textSpan.start
    assert 30 == sent.textSpan.ending
    assert sent.tokenization is None
    sent = sect.sentenceList[1]
    assert 31 == sent.textSpan.start
    assert 31 == sent.textSpan.ending
    assert sent.tokenization is None

    assert validate_communication(comm)
