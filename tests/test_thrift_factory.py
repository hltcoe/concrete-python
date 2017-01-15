from concrete.util.thrift_factory import is_accelerated


def test_is_accelerated():
    assert is_accelerated() in (True, False)
