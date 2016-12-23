import unittest

from concrete.structure.ttypes import (
    TokenizationKind, TokenLattice, LatticePath, Token,
    TokenTagging, TaggedToken, Tokenization
)

from concrete.util.simple_comm import create_comm
from concrete.util.tokenization import (
    get_tokens, get_pos, get_lemmas, get_tagged_tokens
)


class TestTokenization(unittest.TestCase):
    """
    Test suite for module.
    """

    def test_get_tokens_invalid_kind(self):
        self.assertRaises(ValueError,
                          get_tokens,
                          Tokenization(kind='invalid-kind'))


class TestGetTaggedTokens(unittest.TestCase):
    def setUp(self):
        self.tokenization = Tokenization(
            tokenTaggingList=[
                TokenTagging(
                    taggingType='?',
                    taggedTokenList=[
                        TaggedToken(tokenIndex=0, tag='?'),
                        TaggedToken(tokenIndex=1, tag='?'),
                        TaggedToken(tokenIndex=2, tag='?'),
                    ],
                ),
                TokenTagging(
                    taggingType='POS',
                    taggedTokenList=[
                        TaggedToken(tokenIndex=0, tag='N'),
                        TaggedToken(tokenIndex=1, tag='N'),
                        TaggedToken(tokenIndex=2, tag='X'),
                    ],
                ),
                TokenTagging(
                    taggingType='NUMERAL',
                    taggedTokenList=[
                        TaggedToken(tokenIndex=0, tag='N'),
                        TaggedToken(tokenIndex=1, tag='N'),
                        TaggedToken(tokenIndex=2, tag='Y'),
                    ],
                ),
                TokenTagging(
                    taggingType='LEMMA',
                    taggedTokenList=[
                        TaggedToken(tokenIndex=0, tag='mambo'),
                        TaggedToken(tokenIndex=1, tag='number'),
                        TaggedToken(tokenIndex=2, tag='4'),
                    ],
                ),
            ],
        )

    def test_get_pos(self):
        self.assertEqual(
            ['N', 'N', 'X'],
            map(lambda t: t.tag, get_pos(self.tokenization))
        )
        self.assertEqual(
            [0, 1, 2],
            map(lambda t: t.tokenIndex, get_pos(self.tokenization))
        )

    def test_get_pos_no_tagging(self):
        self.tokenization.tokenTaggingList = filter(
            lambda ttl: ttl.taggingType != 'POS',
            self.tokenization.tokenTaggingList
        )
        with self.assertRaises(Exception):
            get_pos(self.tokenization)

    def test_get_pos_non_unique_tagging(self):
        self.tokenization.tokenTaggingList.append(
            TokenTagging(
                taggingType='POS',
                taggedTokenList=[
                    TaggedToken(tokenIndex=0, tag='N'),
                    TaggedToken(tokenIndex=1, tag='X'),
                    TaggedToken(tokenIndex=2, tag='N'),
                ],
            ),
        )
        with self.assertRaises(Exception):
            get_pos(self.tokenization)

    def test_get_lemmas(self):
        self.assertEqual(
            ['mambo', 'number', '4'],
            map(lambda t: t.tag, get_lemmas(self.tokenization))
        )
        self.assertEqual(
            [0, 1, 2],
            map(lambda t: t.tokenIndex, get_lemmas(self.tokenization))
        )

    def test_get_lemmas_no_tagging(self):
        self.tokenization.tokenTaggingList = filter(
            lambda ttl: ttl.taggingType != 'LEMMA',
            self.tokenization.tokenTaggingList
        )
        with self.assertRaises(Exception):
            get_lemmas(self.tokenization)

    def test_get_lemmas_non_unique_tagging(self):
        self.tokenization.tokenTaggingList.append(
            TokenTagging(
                taggingType='LEMMA',
                taggedTokenList=[
                    TaggedToken(tokenIndex=0, tag='mambo'),
                    TaggedToken(tokenIndex=1, tag='number'),
                    TaggedToken(tokenIndex=2, tag='four'),
                ],
            ),
        )
        with self.assertRaises(Exception):
            get_lemmas(self.tokenization)

    def test_get_tagged_tokens(self):
        self.assertEqual(
            ['N', 'N', 'Y'],
            map(lambda t: t.tag, get_tagged_tokens(self.tokenization,
                                                   'NUMERAL'))
        )
        self.assertEqual(
            [0, 1, 2],
            map(lambda t: t.tokenIndex, get_tagged_tokens(self.tokenization,
                                                          'NUMERAL'))
        )

    def test_get_tagged_tokens_no_tagging(self):
        self.tokenization.tokenTaggingList = filter(
            lambda ttl: ttl.taggingType != 'NUMERAL',
            self.tokenization.tokenTaggingList
        )
        with self.assertRaises(Exception):
            get_tagged_tokens(self.tokenization, 'NUMERAL')

    def test_get_tagged_tokens_non_unique_tagging(self):
        self.tokenization.tokenTaggingList.append(
            TokenTagging(
                taggingType='NUMERAL',
                taggedTokenList=[
                    TaggedToken(tokenIndex=0, tag='N'),
                    TaggedToken(tokenIndex=1, tag='Y'),
                    TaggedToken(tokenIndex=2, tag='Y'),
                ],
            ),
        )
        with self.assertRaises(Exception):
            get_tagged_tokens(self.tokenization, 'NUMERAL')


class TestGetTokenList(unittest.TestCase):
    def test_no_lattice(self):
        comm = create_comm('comm-1', 'mambo no. 4')
        tokenization = comm.sectionList[0].sentenceList[0].tokenization
        tokenization.kind = None
        token_texts = [t.text for t in get_tokens(tokenization)]
        self.assertEqual(['mambo', 'no.', '4'], token_texts)

    def test_no_lattice_with_no_kind(self):
        comm = create_comm('comm-1', 'mambo no. 4')
        tokenization = comm.sectionList[0].sentenceList[0].tokenization
        token_texts = [t.text for t in get_tokens(tokenization)]
        self.assertEqual(['mambo', 'no.', '4'], token_texts)

    def test_lattice_with_token_list_kind(self):
        comm = create_comm('comm-1', 'mambo no. 4')
        tokenization = comm.sectionList[0].sentenceList[0].tokenization
        lattice_path = LatticePath()
        lattice_path.tokenList = [Token(tokenIndex=0, text='mambo'),
                                  Token(tokenIndex=0, text='no.'),
                                  Token(tokenIndex=0, text='3')]
        token_lattice = TokenLattice()
        token_lattice.cachedBestPath = lattice_path
        tokenization.lattice = token_lattice
        token_texts = [t.text for t in get_tokens(tokenization)]
        self.assertEqual(['mambo', 'no.', '4'], token_texts)

    def test_lattice_with_token_lattice_kind(self):
        comm = create_comm('comm-1', 'mambo no. 4')
        tokenization = comm.sectionList[0].sentenceList[0].tokenization
        lattice_path = LatticePath()
        lattice_path.tokenList = [Token(tokenIndex=0, text='mambo'),
                                  Token(tokenIndex=0, text='no.'),
                                  Token(tokenIndex=0, text='3')]
        token_lattice = TokenLattice()
        token_lattice.cachedBestPath = lattice_path
        tokenization.lattice = token_lattice
        tokenization.kind = TokenizationKind.TOKEN_LATTICE
        token_texts = [t.text for t in get_tokens(tokenization)]
        self.assertEqual(['mambo', 'no.', '3'], token_texts)

    def test_lattice_with_no_kind(self):
        comm = create_comm('comm-1', 'mambo no. 4')
        tokenization = comm.sectionList[0].sentenceList[0].tokenization
        lattice_path = LatticePath()
        lattice_path.tokenList = [Token(tokenIndex=0, text='mambo'),
                                  Token(tokenIndex=0, text='no.'),
                                  Token(tokenIndex=0, text='3')]
        token_lattice = TokenLattice()
        token_lattice.cachedBestPath = lattice_path
        tokenization.lattice = token_lattice
        tokenization.kind = None
        token_texts = [t.text for t in get_tokens(tokenization)]
        self.assertEqual(['mambo', 'no.', '4'], token_texts)
