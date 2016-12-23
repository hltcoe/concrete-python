import unittest

from concrete.util.mem_io import (
    read_communication_from_buffer,
    write_communication_to_buffer,
    communication_deep_copy
)
from concrete.util.simple_comm import create_comm
from concrete.structure.ttypes import Token


class TestCommunicationDeepCopy(unittest.TestCase):

    def assert_simple_comms_equal(self, comm1, comm2):
        self.assertEquals(comm1.id, comm2.id)
        self.assertEquals(comm1.uuid.uuidString, comm2.uuid.uuidString)
        self.assertEquals(comm1.metadata.tool, comm2.metadata.tool)
        self.assertEquals(comm1.metadata.timestamp, comm2.metadata.timestamp)
        self.assertEquals(
            comm1.sectionList[0].uuid.uuidString,
            comm2.sectionList[0].uuid.uuidString,
        )
        self.assertEquals(
            comm1.sectionList[0].kind,
            comm2.sectionList[0].kind,
        )
        self.assertEquals(
            comm1.sectionList[0].sentenceList[0].uuid.uuidString,
            comm2.sectionList[0].sentenceList[0].uuid.uuidString,
        )
        self.assertEquals(
            comm1.sectionList[0].sentenceList[0].tokenization.uuid,
            comm2.sectionList[0].sentenceList[0].tokenization.uuid,
        )
        self.assertEquals(
            comm1.sectionList[0].sentenceList[0].tokenization.kind,
            comm2.sectionList[0].sentenceList[0].tokenization.kind,
        )
        self.assertEquals(
            comm1.sectionList[0].sentenceList[0].tokenization.metadata.tool,
            comm2.sectionList[0].sentenceList[0].tokenization.metadata.tool,
        )
        self.assertEquals(
            comm1.sectionList[0].sentenceList[
                0].tokenization.metadata.timestamp,
            comm2.sectionList[0].sentenceList[
                0].tokenization.metadata.timestamp,
        )
        self.assertEquals(
            map(lambda t: t.text, comm1.sectionList[0].sentenceList[
                0].tokenization.tokenList.tokenList),
            map(lambda t: t.text, comm2.sectionList[0].sentenceList[
                0].tokenization.tokenList.tokenList),
        )
        self.assertEquals(
            map(lambda t: t.tokenIndex, comm1.sectionList[
                0].sentenceList[0].tokenization.tokenList.tokenList),
            map(lambda t: t.tokenIndex, comm2.sectionList[
                0].sentenceList[0].tokenization.tokenList.tokenList),
        )

    def test_communication_deep_copy(self):
        comm1 = create_comm('a-b-c', text='foo bar baz .')
        comm2 = communication_deep_copy(comm1)
        comm3 = communication_deep_copy(comm1)
        self.assert_simple_comms_equal(comm1, comm2)
        self.assert_simple_comms_equal(comm2, comm3)
        tkzn1 = comm1.sectionList[0].sentenceList[0].tokenization
        tkzn1.tokenList.tokenList[0] = Token(text='bbq', tokenIndex=0)
        tkzn2 = comm2.sectionList[0].sentenceList[0].tokenization
        self.assertNotEqual(
            map(lambda t: t.text, tkzn1.tokenList.tokenList),
            map(lambda t: t.text, tkzn2.tokenList.tokenList),
        )
        self.assert_simple_comms_equal(comm2, comm3)


class TestReadCommunicationFromBuffer(unittest.TestCase):

    def test_read_against_file_contents(self):
        filename = u'tests/testdata/simple_1.concrete'
        with open(filename, 'rb') as f:
            buf = f.read()
            comm = read_communication_from_buffer(buf)
            self.assertTrue(hasattr(comm, 'sentenceForUUID'))
            self.assertEquals('one', comm.id)

    def test_read_against_file_contents_no_add_references(self):
        filename = u'tests/testdata/simple_1.concrete'
        with open(filename, 'rb') as f:
            buf = f.read()
            comm = read_communication_from_buffer(buf, add_references=False)
            self.assertFalse(hasattr(comm, 'sentenceForUUID'))
            self.assertEquals('one', comm.id)


class TestWriteCommunicationToBuffer(unittest.TestCase):

    def test_write_against_file_contents(self):
        filename = u'tests/testdata/simple_1.concrete'
        with open(filename, 'rb') as f:
            f_buf = f.read()
            comm = read_communication_from_buffer(f_buf)
        buf = write_communication_to_buffer(comm)
        self.assertEquals(f_buf, buf)

    def test_read_write_fixed_point(self):
        comm = create_comm('comm-1')
        buf_1 = write_communication_to_buffer(comm)
        buf_2 = write_communication_to_buffer(
            read_communication_from_buffer(buf_1)
        )
        self.assertEquals(buf_1, buf_2)
