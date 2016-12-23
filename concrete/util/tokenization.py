import logging

from concrete.structure.ttypes import TokenizationKind
from concrete.util.unnone import lun


def get_tokens(tokenization, suppress_warnings=False):
    '''
    Return list of Tokens from lattice.cachedBestPath, if Tokenization
    kind is TOKEN_LATTICE; else, return list of Tokens from tokenList.

    Warn and return list of Tokens from tokenList if kind is not set.
    Return None if kind is set but the respective data fields are not.
    '''

    if tokenization.kind is None:
        if not suppress_warnings:
            logging.warn('Tokenization.kind is None but is required in '
                         'Concrete; using tokenList')

        token_list = tokenization.tokenList
        if token_list.tokenList is not None:
            return token_list.tokenList

    elif tokenization.kind == TokenizationKind.TOKEN_LATTICE:
        token_lattice = tokenization.lattice
        if token_lattice.cachedBestPath is not None:
            lattice_path = token_lattice.cachedBestPath
            if lattice_path.tokenList is not None:
                return lattice_path.tokenList

    elif tokenization.kind == TokenizationKind.TOKEN_LIST:
        token_list = tokenization.tokenList
        if token_list.tokenList is not None:
            return token_list.tokenList

    else:
        raise ValueError('Unrecognized TokenizationKind %s'
                         % tokenization.kind)

    return None


def get_tagged_tokens(tokenization, tagging_type):
    '''
    Return list of TaggedTokens of taggingType equal to tagging_type,
    if there is a unique choice.

    Raise exception if there is no matching tagging or more than one
    matching tagging.
    '''
    tts = [
        tt
        for tt in tokenization.tokenTaggingList
        if tt.taggingType == tagging_type
    ]
    if len(tts) == 0:
        raise Exception('No %s tagging.' % tagging_type)
    elif len(tts) == 1:
        return tts[0].taggedTokenList
    else:
        raise Exception('More than one %s tagging.' % tagging_type)


def get_lemmas(t):
    return get_tagged_tokens(t, 'LEMMA')


def get_pos(t):
    return get_tagged_tokens(t, 'POS')


def plus(x, y):
    return x + y


def flatten(a):
    return reduce(plus, a, [])


def get_comm_tokens(comm, sect_pred=None, suppress_warnings=False):
    '''
    Return list of Tokens in communication, delegating to get_tokens
    for each sentence.
    '''
    return flatten(map(
        lambda sect: flatten(map(
            lambda sent: get_tokens(sent.tokenization, suppress_warnings),
            sect.sentenceList
        )),
        filter(sect_pred, comm.sectionList)
        if (sect_pred is not None) else comm.sectionList
    ))


def get_comm_tokenizations(comm, tool=None):
    for section in lun(comm.sectionList):
        for sentence in lun(section.sentenceList):
            if tool is None or sentence.tokenization.metadata.tool == tool:
                yield sentence.tokenization


def latticeToFsm(lattice, is_cost=True):
    '''
    Author: Adrian Benton
    '''
    fsm = {}
    bkFsm = {}

    tokens = set()
    states = set()
    for arc in lattice.arcList:
        src, dst, token, wt = arc.src, arc.dst, arc.token.text, arc.weight
        tokens.add(token)
        states.add(src)
        states.add(dst)

        if is_cost:  # Treat as log-probs instead
            wt = -wt

        if src not in fsm:
            fsm[src] = {}
        if dst not in fsm[src]:
            fsm[src][dst] = []
        fsm[src][dst].append((token, wt))

        if dst not in bkFsm:
            bkFsm[dst] = {}
        if src not in bkFsm[dst]:
            bkFsm[dst][src] = []
        bkFsm[dst][src].append((token, wt))

    return fsm, bkFsm, tokens, states


def calc_alpha(fsm, states, start, end):
    '''
    Calculates total in-probability of each state.  Assumes weights are
    log-probbish
    Author: Adrian Benton
    '''

    from scipy.misc import logsumexp

    alpha = {}
    alpha[start] = 0.

    for state in states:
        currState = state

        if currState == end:
            continue

        arcs = fsm[currState]

        for dst, tokenWts in arcs.items():
            if dst not in alpha:
                alpha[dst] = float('-inf')
            for token, wt in tokenWts:
                alpha[dst] = logsumexp([alpha[dst], alpha[currState] + wt])

    return alpha


def calc_beta(bkFsm, states, end, start):
    '''
    Calculates total out-probability of each state.  Assumes weights are
    log-probbish
    Author: Adrian Benton
    '''

    from scipy.misc import logsumexp

    beta = {}
    beta[end] = 0.

    for state in sorted(states, reverse=True):
        currState = state

        if currState == start:
            continue

        arcs = bkFsm[currState]

        for src, tokenWts in arcs.items():
            if src not in beta:
                beta[src] = float('-inf')
            for token, wt in tokenWts:
                beta[src] = logsumexp([beta[src], beta[currState] + wt])

    return beta


def get_norm(alpha, beta, start, end):
    '''
    Author: Adrian Benton
    '''
    return alpha[end]


def compute_lattice_expected_counts(lattice, is_cost=True):
    '''
    Assumes that edge weights are in log-space (may be + or -).
    Author: Adrian Benton
    '''

    from scipy.misc import logsumexp

    fsm, bkFsm, tokens, states = latticeToFsm(lattice, is_cost=is_cost)
    states = sorted(list(states))
    alpha = calc_alpha(fsm, states, lattice.startState, lattice.endState)
    beta = calc_beta(bkFsm, states, lattice.endState, lattice.startState)
    norm = get_norm(alpha, beta, lattice.startState, lattice.endState)

    expectedCounts = {}

    for state in states:
        currState = state

        if currState == lattice.endState:
            continue

        arcs = fsm[currState]

        for dst, tokenWts in arcs.items():
            for token, wt in tokenWts:
                if token not in expectedCounts:
                    expectedCounts[token] = []
                expectedCounts[token].append(
                    alpha[currState] + beta[dst] + wt - norm)

    for token in expectedCounts:
        expectedCounts[token] = logsumexp(expectedCounts[token])

    return expectedCounts
