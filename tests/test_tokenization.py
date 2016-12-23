from pytest import raises, fixture

from math import exp, log

from concrete.structure.ttypes import (
    TokenizationKind, TokenLattice, LatticePath, Token,
    TokenTagging, TaggedToken, Tokenization, Arc
)

from concrete.util.simple_comm import create_comm
from concrete.util.tokenization import (
    get_tokens, get_pos, get_lemmas, get_tagged_tokens,
    compute_lattice_expected_counts
)


def allclose(x, y, rel_tol=1e-6, abs_tol=1e-9):
    return (
        len(x) == len(y) and
        len(x) == sum(
            abs(x[i] - y[i]) <= rel_tol * abs(x[i]) + abs_tol
            for i in xrange(len(x))
        )
    )


@fixture
def tokenization(request):
    return Tokenization(
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


def test_get_tokens_invalid_kind():
    with raises(ValueError):
        get_tokens(Tokenization(kind='invalid-kind'))


def test_get_pos(tokenization):
    assert ['N', 'N', 'X'] == map(lambda t: t.tag, get_pos(tokenization))
    assert [0, 1, 2] == map(lambda t: t.tokenIndex, get_pos(tokenization))


def test_get_pos_no_tagging(tokenization):
    tokenization.tokenTaggingList = filter(
        lambda ttl: ttl.taggingType != 'POS',
        tokenization.tokenTaggingList
    )
    with raises(Exception):
        get_pos(tokenization)


def test_get_pos_non_unique_tagging(tokenization):
    tokenization.tokenTaggingList.append(
        TokenTagging(
            taggingType='POS',
            taggedTokenList=[
                TaggedToken(tokenIndex=0, tag='N'),
                TaggedToken(tokenIndex=1, tag='X'),
                TaggedToken(tokenIndex=2, tag='N'),
            ],
        ),
    )
    with raises(Exception):
        get_pos(tokenization)


def test_get_lemmas(tokenization):
    assert ['mambo', 'number', '4'] == map(
        lambda t: t.tag,
        get_lemmas(tokenization))
    assert [0, 1, 2] == map(lambda t: t.tokenIndex, get_lemmas(tokenization))


def test_get_lemmas_no_tagging(tokenization):
    tokenization.tokenTaggingList = filter(
        lambda ttl: ttl.taggingType != 'LEMMA',
        tokenization.tokenTaggingList
    )
    with raises(Exception):
        get_lemmas(tokenization)


def test_get_lemmas_non_unique_tagging(tokenization):
    tokenization.tokenTaggingList.append(
        TokenTagging(
            taggingType='LEMMA',
            taggedTokenList=[
                TaggedToken(tokenIndex=0, tag='mambo'),
                TaggedToken(tokenIndex=1, tag='number'),
                TaggedToken(tokenIndex=2, tag='four'),
            ],
        ),
    )
    with raises(Exception):
        get_lemmas(tokenization)


def test_get_tagged_tokens(tokenization):
    assert ['N', 'N', 'Y'] == map(
        lambda t: t.tag,
        get_tagged_tokens(tokenization, 'NUMERAL'))
    assert [0, 1, 2] == map(
        lambda t: t.tokenIndex,
        get_tagged_tokens(tokenization, 'NUMERAL'))


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
