from concrete.util import read_communication_from_file


def read_test_comm():
    communication_filename = "tests/testdata/serif_dog-bites-man.concrete"
    return read_communication_from_file(communication_filename)
