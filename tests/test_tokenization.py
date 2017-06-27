from __future__ import unicode_literals
from pytest import raises, fixture

from math import exp, log

from concrete import (
    TokenizationKind, TokenLattice, LatticePath, Token,
    TokenTagging, TaggedToken, Tokenization, Arc,
    AnnotationMetadata
)

from concrete.util import create_comm
from concrete.util import (
    get_tokens, get_ner, get_pos, get_lemmas, get_tagged_tokens,
    compute_lattice_expected_counts, get_token_taggings
)

import mock


def allclose(x, y, rel_tol=1e-6, abs_tol=1e-9):
    return (
        len(x) == len(y) and
        len(x) == sum(
            abs(x[i] - y[i]) <= rel_tol * abs(x[i]) + abs_tol
            for i in range(len(x))
        )
    )


@fixture
def tokenization(request):
    return Tokenization(
        tokenTaggingList=[
            TokenTagging(
                metadata=AnnotationMetadata(tool='x'),
                taggingType='?',
                taggedTokenList=[
                    TaggedToken(tokenIndex=0, tag='?'),
                    TaggedToken(tokenIndex=1, tag='?'),
                    TaggedToken(tokenIndex=2, tag='?'),
                ],
            ),
            TokenTagging(
                metadata=AnnotationMetadata(tool='x'),
                taggingType='POS',
                taggedTokenList=[
                    TaggedToken(tokenIndex=0, tag='N'),
                    TaggedToken(tokenIndex=1, tag='N'),
                    TaggedToken(tokenIndex=2, tag='X'),
                ],
            ),
            TokenTagging(
                metadata=AnnotationMetadata(tool='y'),
                taggingType='NUMERAL',
                taggedTokenList=[
                    TaggedToken(tokenIndex=0, tag='N'),
                    TaggedToken(tokenIndex=1, tag='N'),
                    TaggedToken(tokenIndex=2, tag='Y'),
                ],
            ),
            TokenTagging(
                metadata=AnnotationMetadata(tool='y'),
                taggingType='LEMMA',
                taggedTokenList=[
                    TaggedToken(tokenIndex=0, tag='mambo'),
                    TaggedToken(tokenIndex=1, tag='number'),
                    TaggedToken(tokenIndex=2, tag='4'),
                ],
            ),
        ],
    )


def test_get_tokens_invalid_kind():
    with raises(ValueError):
        get_tokens(Tokenization(kind='invalid-kind'))


@mock.patch('concrete.util.tokenization.get_tagged_tokens')
def test_get_pos(mock_get_tagged_tokens):
    tokenization = mock.sentinel
    tool = mock.sentinel
    get_pos(tokenization, tool=tool)
    mock_get_tagged_tokens.assert_called_with(tokenization, 'POS', tool=tool)


@mock.patch('concrete.util.tokenization.get_tagged_tokens')
def test_get_lemmas(mock_get_tagged_tokens):
    tokenization = mock.sentinel
    tool = mock.sentinel
    get_lemmas(tokenization, tool=tool)
    mock_get_tagged_tokens.assert_called_with(tokenization, 'LEMMA', tool=tool)


@mock.patch('concrete.util.tokenization.get_tagged_tokens')
def test_get_ner(mock_get_tagged_tokens):
    tokenization = mock.sentinel
    tool = mock.sentinel
    get_ner(tokenization, tool=tool)
    mock_get_tagged_tokens.assert_called_with(tokenization, 'NER', tool=tool)


def test_get_tagged_tokens(tokenization):
    assert ['N', 'N', 'Y'] == list(map(
        lambda t: t.tag,
        get_tagged_tokens(tokenization, 'NUMERAL')))
    assert [0, 1, 2] == list(map(
        lambda t: t.tokenIndex,
        get_tagged_tokens(tokenization, 'NUMERAL')))


def test_get_tagged_tokens_lowercase(tokenization):
    assert ['N', 'N', 'Y'] == list(map(
        lambda t: t.tag,
        get_tagged_tokens(tokenization, 'numeral')))
    assert [0, 1, 2] == list(map(
        lambda t: t.tokenIndex,
        get_tagged_tokens(tokenization, 'numeral')))


def test_get_tagged_tokens_no_tagging(tokenization):
    tokenization.tokenTaggingList = filter(
        lambda ttl: ttl.taggingType != 'NUMERAL',
        tokenization.tokenTaggingList
    )
    with raises(Exception):
        get_tagged_tokens(tokenization, 'NUMERAL')


def test_get_tagged_tokens_non_unique_tagging(tokenization):
    tokenization.tokenTaggingList.append(
        TokenTagging(
            taggingType='NUMERAL',
            taggedTokenList=[
                TaggedToken(tokenIndex=0, tag='N'),
                TaggedToken(tokenIndex=1, tag='Y'),
                TaggedToken(tokenIndex=2, tag='Y'),
            ],
        ),
    )
    with raises(Exception):
        get_tagged_tokens(tokenization, 'NUMERAL')


def test_get_tagged_tokens_non_unique_tagging_specify_tool(tokenization):
    tokenization.tokenTaggingList.append(
        TokenTagging(
            metadata=AnnotationMetadata(tool='z'),
            taggingType='NUMERAL',
            taggedTokenList=[
                TaggedToken(tokenIndex=0, tag='N'),
                TaggedToken(tokenIndex=1, tag='Y'),
                TaggedToken(tokenIndex=2, tag='Y'),
            ],
        ),
    )
    assert ['N', 'N', 'Y'] == list(map(
        lambda t: t.tag,
        get_tagged_tokens(tokenization, 'NUMERAL', tool='y')))
    assert [0, 1, 2] == list(map(
        lambda t: t.tokenIndex,
        get_tagged_tokens(tokenization, 'NUMERAL', tool='y')))


def test_get_tagged_tokens_non_unique_tagging_specify_tool_uppercase(tokenization):
    tokenization.tokenTaggingList.append(
        TokenTagging(
            metadata=AnnotationMetadata(tool='Z'),
            taggingType='NUMERAL',
            taggedTokenList=[
                TaggedToken(tokenIndex=0, tag='N'),
                TaggedToken(tokenIndex=1, tag='Y'),
                TaggedToken(tokenIndex=2, tag='Y'),
            ],
        ),
    )
    assert ['N', 'N', 'Y'] == list(map(
        lambda t: t.tag,
        get_tagged_tokens(tokenization, 'NUMERAL', tool='y')))
    assert [0, 1, 2] == list(map(
        lambda t: t.tokenIndex,
        get_tagged_tokens(tokenization, 'NUMERAL', tool='y')))


def test_get_tagged_tokens_no_tagging_specify_tool(tokenization):
    with raises(Exception):
        get_tagged_tokens(tokenization, 'NUMERAL', tool='z')


def test_get_token_taggings(tokenization):
    assert [[(0, 'N'), (1, 'N'), (2, 'Y')]] == [
        [(t.tokenIndex, t.tag) for t in tt.taggedTokenList]
        for tt in get_token_taggings(tokenization, 'NUMERAL')
    ]


def test_get_token_taggings_lowercase(tokenization):
    assert [[(0, 'N'), (1, 'N'), (2, 'Y')]] == [
        [(t.tokenIndex, t.tag) for t in tt.taggedTokenList]
        for tt in get_token_taggings(tokenization, 'numeral')
    ]


def test_get_token_taggings_lowercase_case_sensitive(tokenization):
    assert [] == get_token_taggings(tokenization, 'numeral',
                                    case_sensitive=True)


def test_get_token_taggings_no_tagging(tokenization):
    assert [] == get_token_taggings(tokenization, '!NUMERAL')


def test_get_token_taggings_non_unique_tagging(tokenization):
    tokenization.tokenTaggingList.append(
        TokenTagging(
            taggingType='NUMERAL',
            taggedTokenList=[
                TaggedToken(tokenIndex=0, tag='N'),
                TaggedToken(tokenIndex=1, tag='Y'),
                TaggedToken(tokenIndex=2, tag='Y'),
            ],
        ),
    )
    assert [
        [(0, 'N'), (1, 'N'), (2, 'Y')],
        [(0, 'N'), (1, 'Y'), (2, 'Y')],
    ] == [
        [(t.tokenIndex, t.tag) for t in tt.taggedTokenList]
        for tt in get_token_taggings(tokenization, 'NUMERAL')
    ]


def test_no_lattice():
    comm = create_comm('comm-1', 'mambo no. 4')
    tokenization = comm.sectionList[0].sentenceList[0].tokenization
    tokenization.kind = None
    token_texts = [t.text for t in get_tokens(tokenization)]
    assert ['mambo', 'no.', '4'] == token_texts


def test_no_lattice_with_no_kind():
    comm = create_comm('comm-1', 'mambo no. 4')
    tokenization = comm.sectionList[0].sentenceList[0].tokenization
    token_texts = [t.text for t in get_tokens(tokenization)]
    assert ['mambo', 'no.', '4'] == token_texts


def test_lattice_with_token_list_kind():
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
    assert ['mambo', 'no.', '4'] == token_texts


def test_lattice_with_token_lattice_kind():
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
    assert ['mambo', 'no.', '3'] == token_texts


def test_lattice_with_no_kind():
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
    assert ['mambo', 'no.', '4'] == token_texts


def test_compute_lattice_expected_counts_empty():
    assert compute_lattice_expected_counts(TokenLattice(arcList=[
    ], startState=0, endState=0)) == []


def test_compute_lattice_expected_counts_one_arc():
    # 0 --0-> 1, -1
    expected = [0.]
    actual = compute_lattice_expected_counts(TokenLattice(arcList=[
        Arc(src=0, dst=1, token=Token(tokenIndex=0), weight=-1.),
    ], startState=0, endState=1))
    assert allclose(expected, actual), '%s !~= %s' % (expected, actual)


def test_compute_lattice_expected_counts_two_parallel_arcs():
    # 0 --0-> 1, -1
    # 0 --0-> 1, -3
    expected = [0.]
    actual = compute_lattice_expected_counts(TokenLattice(arcList=[
        Arc(src=0, dst=1, token=Token(tokenIndex=0), weight=-1.),
        Arc(src=0, dst=1, token=Token(tokenIndex=0), weight=-3.),
    ], startState=0, endState=1))
    assert allclose(expected, actual), '%s !~= %s' % (expected, actual)


def test_compute_lattice_expected_counts_two_serial_arcs():
    # 0 --0-> 1, -1
    # 1 --1-> 2, -3
    expected = [0., 0.]
    actual = compute_lattice_expected_counts(TokenLattice(arcList=[
        Arc(src=0, dst=1, token=Token(tokenIndex=0), weight=-1.),
        Arc(src=1, dst=2, token=Token(tokenIndex=1), weight=-3.),
    ], startState=0, endState=2))
    assert allclose(expected, actual), '%s !~= %s' % (expected, actual)


def test_compute_lattice_expected_counts_triangle():
    # 0 --0-> 1, -1
    # 1 --1-> 2, -2
    # 0 --1-> 2, -4
    A = log(exp(-1 + -2) + exp(-4))
    expected = [-1 + -2 - A, 0.]
    actual = compute_lattice_expected_counts(TokenLattice(arcList=[
        Arc(src=0, dst=1, token=Token(tokenIndex=0), weight=-1.),
        Arc(src=1, dst=2, token=Token(tokenIndex=1), weight=-2.),
        Arc(src=0, dst=2, token=Token(tokenIndex=1), weight=-4.),
    ], startState=0, endState=2))
    assert allclose(expected, actual), '%s !~= %s' % (expected, actual)


def test_compute_lattice_expected_counts_triangle_arbitrary_states():
    # 47 --0-> 9, -1
    #  9 --1-> 3, -2
    # 47 --1-> 3, -4
    A = log(exp(-1 + -2) + exp(-4))
    expected = [-1 + -2 - A, 0.]
    actual = compute_lattice_expected_counts(TokenLattice(arcList=[
        Arc(src=47, dst=9, token=Token(tokenIndex=0), weight=-1.),
        Arc(src=9, dst=3, token=Token(tokenIndex=1), weight=-2.),
        Arc(src=47, dst=3, token=Token(tokenIndex=1), weight=-4.),
    ], startState=47, endState=3))
    assert allclose(expected, actual), '%s !~= %s' % (expected, actual)


def test_compute_lattice_expected_counts_rhombus():
    # 0 --0-> 1, -1
    # 1 --1-> 3, -2
    # 0 --0-> 2, -3
    # 2 --2-> 3, -4
    A = log(exp(-1 + -2) + exp(-3 + -4))
    expected = [0., -1 + -2 - A, -3 + -4 - A]
    actual = compute_lattice_expected_counts(TokenLattice(arcList=[
        Arc(src=0, dst=1, token=Token(tokenIndex=0), weight=-1.),
        Arc(src=1, dst=3, token=Token(tokenIndex=1), weight=-2.),
        Arc(src=0, dst=2, token=Token(tokenIndex=0), weight=-3.),
        Arc(src=2, dst=3, token=Token(tokenIndex=2), weight=-4.),
    ], startState=0, endState=3))
    assert allclose(expected, actual), '%s !~= %s' % (expected, actual)


def test_compute_lattice_expected_counts_incomplete_arc():
    # 0 --0-> 1, -1
    with raises(ValueError):
        compute_lattice_expected_counts(TokenLattice(arcList=[
            Arc(dst=1, token=Token(tokenIndex=0), weight=-1.),
        ], startState=0, endState=1))
    with raises(ValueError):
        compute_lattice_expected_counts(TokenLattice(arcList=[
            Arc(src=0, token=Token(tokenIndex=0), weight=-1.),
        ], startState=0, endState=1))
    with raises(ValueError):
        compute_lattice_expected_counts(TokenLattice(arcList=[
            Arc(src=0, dst=1, weight=-1.),
        ], startState=0, endState=1))
    with raises(ValueError):
        compute_lattice_expected_counts(TokenLattice(arcList=[
            Arc(src=0, dst=1, token=Token(tokenIndex=0)),
        ], startState=0, endState=1))
