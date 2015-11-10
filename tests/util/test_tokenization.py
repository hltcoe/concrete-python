import unittest

from concrete.structure.ttypes import Tokenization, TokenizationKind
from concrete.util import tokenization


class TestTokenization(unittest.TestCase):
    """
    Test suite for module.
    """

    def test_get_tokens_invalid_kind(self):
        self.assertRaises(ValueError,
                          tokenization.get_tokens,
                          Tokenization(kind='invalid-kind'))
