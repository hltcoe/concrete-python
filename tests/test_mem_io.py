from __future__ import unicode_literals

from concrete.util import (
    read_communication_from_buffer,
    write_communication_to_buffer,
    communication_deep_copy
)
from concrete.util import create_comm
from concrete import Token


def assert_simple_comms_equal(comm1, comm2):
    assert comm1.id == comm2.id
    assert comm1.uuid.uuidString == comm2.uuid.uuidString
    assert comm1.metadata.tool == comm2.metadata.tool
    assert comm1.metadata.timestamp == comm2.metadata.timestamp
    assert (
        comm1.sectionList[0].uuid.uuidString ==
        comm2.sectionList[0].uuid.uuidString
    )
    assert (
        comm1.sectionList[0].kind ==
        comm2.sectionList[0].kind
    )
    assert (
        comm1.sectionList[0].sentenceList[0].uuid.uuidString ==
        comm2.sectionList[0].sentenceList[0].uuid.uuidString
    )
    assert (
        comm1.sectionList[0].sentenceList[0].tokenization.uuid ==
        comm2.sectionList[0].sentenceList[0].tokenization.uuid
    )
    assert (
        comm1.sectionList[0].sentenceList[0].tokenization.kind ==
        comm2.sectionList[0].sentenceList[0].tokenization.kind
    )
    assert (
        comm1.sectionList[0].sentenceList[0].tokenization.metadata.tool ==
        comm2.sectionList[0].sentenceList[0].tokenization.metadata.tool
    )
    assert (
        comm1.sectionList[0].sentenceList[0].tokenization.metadata.timestamp ==
        comm2.sectionList[0].sentenceList[0].tokenization.metadata.timestamp
    )
    assert list(map(
        lambda t: (t.text, t.tokenIndex),
        comm1.sectionList[0].sentenceList[0].tokenization.tokenList.tokenList
    )) == list(map(
        lambda t: (t.text, t.tokenIndex),
        comm2.sectionList[0].sentenceList[0].tokenization.tokenList.tokenList
    ))


def test_communication_deep_copy():
    comm1 = create_comm('a-b-c', text='foo bar baz .')
    comm2 = communication_deep_copy(comm1)
    comm3 = communication_deep_copy(comm1)
    assert_simple_comms_equal(comm1, comm2)
    assert_simple_comms_equal(comm2, comm3)
    tkzn1 = comm1.sectionList[0].sentenceList[0].tokenization
    tkzn1.tokenList.tokenList[0] = Token(text='bbq', tokenIndex=0)
    tkzn2 = comm2.sectionList[0].sentenceList[0].tokenization
    assert list(map(
        lambda t: t.text, tkzn1.tokenList.tokenList
    )) != list(map(
        lambda t: t.text, tkzn2.tokenList.tokenList
    ))
    assert_simple_comms_equal(comm2, comm3)


def test_read_against_file_contents():
    filename = u'tests/testdata/simple_1.concrete'
    with open(filename, 'rb') as f:
        buf = f.read()
        comm = read_communication_from_buffer(buf)
        assert hasattr(comm, 'sentenceForUUID')
        assert 'one' == comm.id


def test_read_against_file_contents_no_add_references():
    filename = u'tests/testdata/simple_1.concrete'
    with open(filename, 'rb') as f:
        buf = f.read()
        comm = read_communication_from_buffer(buf, add_references=False)
        assert not hasattr(comm, 'sentenceForUUID')
        assert 'one' == comm.id


def test_write_against_file_contents():
    filename = u'tests/testdata/simple_1.concrete'
    with open(filename, 'rb') as f:
        f_buf = f.read()
        comm = read_communication_from_buffer(f_buf)
    buf = write_communication_to_buffer(comm)
    assert f_buf == buf


def test_read_write_fixed_point():
    comm = create_comm('comm-1')
    buf_1 = write_communication_to_buffer(comm)
    buf_2 = write_communication_to_buffer(
        read_communication_from_buffer(buf_1)
    )
    assert buf_1 == buf_2
