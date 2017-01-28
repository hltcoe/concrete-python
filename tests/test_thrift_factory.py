from __future__ import unicode_literals
from concrete.util import is_accelerated


def test_is_accelerated():
    assert is_accelerated() in (True, False)
