#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""
"""

import unittest

from concrete.validate import validate_communication
from concrete.util import CommunicationReader

from concrete.util.simple_comm import (
        create_comm, create_simple_comm, SimpleCommTempFile
        )

class TestCreateSimpleComm(unittest.TestCase):
    def test_create_simple_comm(self):
        comm = create_simple_comm('one')
        self.assertEqual('one', comm.id)
        self.assertEqual('Super simple sentence .', comm.text)
        self.assertTrue(validate_communication(comm))

class TestCreateComm(unittest.TestCase):
    def test_create_comm_empty(self):
        comm = create_comm('one')
        self.assertEqual('one', comm.id)
        self.assertEqual('', comm.text)
        self.assertEqual(None, comm.sectionList)
        self.assertTrue(validate_communication(comm))

    def test_create_comm_ws(self):
        comm = create_comm('one', '\t \t\r\n\n')
        self.assertEqual('one', comm.id)
        self.assertEqual('\t \t\r\n\n', comm.text)
        self.assertEqual(None, comm.sectionList)
        self.assertTrue(validate_communication(comm))

    def test_create_comm_unicode(self):
        comm = create_comm('one', u'狐狸\t\t.')
        self.assertEqual('one', comm.id)
        self.assertEqual(u'狐狸\t\t.', comm.text)
        self.assertEqual(1, len(comm.sectionList))
        sect = comm.sectionList[0]
        self.assertEqual(0, sect.textSpan.start)
        self.assertEqual(5, sect.textSpan.ending)
        self.assertEqual(1, len(sect.sentenceList))
        sent = sect.sentenceList[0]
        self.assertEqual(0, sent.textSpan.start)
        self.assertEqual(5, sent.textSpan.ending)
        tl = sent.tokenization.tokenList.tokenList
        self.assertEqual(2, len(tl))
        self.assertEqual(0, tl[0].tokenIndex)
        self.assertEqual(u'狐狸', tl[0].text)
        self.assertEqual(1, tl[1].tokenIndex)
        self.assertEqual('.', tl[1].text)
        self.assertTrue(validate_communication(comm))

    def test_create_comm_one_sentence(self):
        comm = create_comm('one', 'simple comm\t\t.')
        self.assertEqual('one', comm.id)
        self.assertEqual('simple comm\t\t.', comm.text)
        self.assertEqual(1, len(comm.sectionList))
        sect = comm.sectionList[0]
        self.assertEqual(0, sect.textSpan.start)
        self.assertEqual(14, sect.textSpan.ending)
        self.assertEqual(1, len(sect.sentenceList))
        sent = sect.sentenceList[0]
        self.assertEqual(0, sent.textSpan.start)
        self.assertEqual(14, sent.textSpan.ending)
        tl = sent.tokenization.tokenList.tokenList
        self.assertEqual(3, len(tl))
        self.assertEqual(0, tl[0].tokenIndex)
        self.assertEqual('simple', tl[0].text)
        self.assertEqual(1, tl[1].tokenIndex)
        self.assertEqual('comm', tl[1].text)
        self.assertEqual(2, tl[2].tokenIndex)
        self.assertEqual('.', tl[2].text)
        self.assertTrue(validate_communication(comm))

    def test_create_comm_complex(self):
        comm = create_comm('one', '\n\nsimple comm\t\t.\nor ...\n\nisit?\n')
        self.assertEqual('one', comm.id)
        self.assertEqual('\n\nsimple comm\t\t.\nor ...\n\nisit?\n', comm.text)
        self.assertEqual(3, len(comm.sectionList))

        sect = comm.sectionList[0]
        self.assertEqual(0, sect.textSpan.start)
        self.assertEqual(0, sect.textSpan.ending)
        self.assertEqual(0, len(sect.sentenceList))

        sect = comm.sectionList[1]
        self.assertEqual(2, sect.textSpan.start)
        self.assertEqual(23, sect.textSpan.ending)
        self.assertEqual(2, len(sect.sentenceList))
        sent = sect.sentenceList[0]
        self.assertEqual(2, sent.textSpan.start)
        self.assertEqual(16, sent.textSpan.ending)
        tl = sent.tokenization.tokenList.tokenList
        self.assertEqual(3, len(tl))
        self.assertEqual(0, tl[0].tokenIndex)
        self.assertEqual('simple', tl[0].text)
        self.assertEqual(1, tl[1].tokenIndex)
        self.assertEqual('comm', tl[1].text)
        self.assertEqual(2, tl[2].tokenIndex)
        self.assertEqual('.', tl[2].text)
        sent = sect.sentenceList[1]
        self.assertEqual(17, sent.textSpan.start)
        self.assertEqual(23, sent.textSpan.ending)
        tl = sent.tokenization.tokenList.tokenList
        self.assertEqual(2, len(tl))
        self.assertEqual(0, tl[0].tokenIndex)
        self.assertEqual('or', tl[0].text)
        self.assertEqual(1, tl[1].tokenIndex)
        self.assertEqual('...', tl[1].text)

        sect = comm.sectionList[2]
        self.assertEqual(25, sect.textSpan.start)
        self.assertEqual(31, sect.textSpan.ending)
        self.assertEqual(2, len(sect.sentenceList))
        sent = sect.sentenceList[0]
        self.assertEqual(25, sent.textSpan.start)
        self.assertEqual(30, sent.textSpan.ending)
        tl = sent.tokenization.tokenList.tokenList
        self.assertEqual(1, len(tl))
        self.assertEqual(0, tl[0].tokenIndex)
        self.assertEqual('isit?', tl[0].text)
        sent = sect.sentenceList[1]
        self.assertEqual(31, sent.textSpan.start)
        self.assertEqual(31, sent.textSpan.ending)
        tl = sent.tokenization.tokenList.tokenList
        self.assertEqual(0, len(tl))

        self.assertTrue(validate_communication(comm))


if __name__ == '__main__':
    unittest.main(buffer=True)
