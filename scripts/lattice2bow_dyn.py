from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from concrete.structure.ttypes import TokenLattice

import math

from numpy import logaddexp
from scipy.misc import logsumexp

'''
Assumes that edge weights are in log-space (may be + or -).

Adrian Benton
'''


def log_sum(x, y):
    return logaddexp(x, y)


def load_lattice(input_path):
    with open(input_path, 'rb') as f:
        transportIn = TTransport.TFileObjectTransport(f)
        protocolIn = TBinaryProtocol.TBinaryProtocol(transportIn)
        lattice = TokenLattice()
        lattice.read(protocolIn)
        return lattice


def latticeToFsm(lattice, isCost=True):
    fsm = {}
    bkFsm = {}

    tokens = set()
    states = set()
    for arc in lattice.arcList:
        src, dst, token, wt = arc.src, arc.dst, arc.token.text, arc.weight
        tokens.add(token)
        states.add(src)
        states.add(dst)

        if isCost:  # Treat as log-probs instead
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
    # Calculates total in-probability of each state.  Assumes weights are
    # log-probbish
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
                alpha[dst] = log_sum(alpha[dst], alpha[currState] + wt)

    return alpha


def calc_beta(bkFsm, states, end, start):
    # Calculates total out-probability of each state.  Assumes weights are
    # log-probbish
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
                beta[src] = log_sum(beta[src], beta[currState] + wt)

    return beta


def get_norm(alpha, beta, start, end):
    return alpha[end]


def compute_lattice_expected_counts(lattice, IS_COST, printOut=True):
    fsm, bkFsm, tokens, states = latticeToFsm(lattice, IS_COST)
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

    if printOut:
        sortedTokens = [(wt, token) for token, wt in expectedCounts.items()]
        sortedTokens.sort(reverse=True)

        for wt, token in sortedTokens:
            print '%.9f\t%s' % (math.exp(expectedCounts[token]), token)

    return expectedCounts


def test():
    test_lattice = load_lattice(
        '/export/a01/abenton/mono0a_test_lattices/'
        '19960605_CNN_HDL-00589876-00604409.lat')
    # test_lattice = load_lattice('gten_2502_9.concrete')
    # test_lattice = load_lattice('testLattice2.concrete')
    compute_lattice_expected_counts(test_lattice, IS_COST=False, printOut=True)


def main():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.set_defaults(raw=False, best=False)
    parser.add_argument('input_path', type=str,
                        help='path to serialized concrete TokenLattice')
    parser.add_argument('--cost', action='store_true',
                        help='weights are costs (positive values, may be >1)')
    args = parser.parse_args()

    lattice = load_lattice(args.input_path)
    compute_lattice_expected_counts(lattice, args.cost)


if __name__ == '__main__':
    # test()
    main()
