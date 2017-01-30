from concrete.util import lun, dun, sun


def test_lun():
    assert lun([]) == []
    assert lun([3]) == [3]
    assert lun(None) == []


def test_dun():
    assert dun(dict()) == dict()
    assert dun(dict(x=3)) == dict(x=3)
    assert dun(None) == dict()


def test_sun():
    assert sun(set([])) == set([])
    assert sun(set([3])) == set([3])
    assert sun(None) == set([])
