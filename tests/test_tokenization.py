#!/usr/bin/env python

import unittest

from concrete import TokenizationKind, TokenLattice, LatticePath, Token

from concrete.util import get_tokens
from concrete.util.simple_comm import create_simple_comm

class TestGetTokenList(unittest.TestCase):
    def test_no_lattice(self):
        comm = create_simple_comm('comm-1', sentence_string='mambo no. 4')
        tokenization = comm.sectionList[0].sentenceList[0].tokenization
        tokenization.kind = None
        token_texts = [t.text for t in get_tokens(tokenization)]
        self.assertEqual(['mambo', 'no.', '4'], token_texts)

    def test_no_lattice_with_no_kind(self):
        comm = create_simple_comm('comm-1', sentence_string='mambo no. 4')
        tokenization = comm.sectionList[0].sentenceList[0].tokenization
        token_texts = [t.text for t in get_tokens(tokenization)]
        self.assertEqual(['mambo', 'no.', '4'], token_texts)

    def test_lattice_with_token_list_kind(self):
        comm = create_simple_comm('comm-1', sentence_string='mambo no. 4')
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
        comm = create_simple_comm('comm-1', sentence_string='mambo no. 4')
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
        comm = create_simple_comm('comm-1', sentence_string='mambo no. 4')
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


if __name__ == '__main__':
    unittest.main(buffer=True)
