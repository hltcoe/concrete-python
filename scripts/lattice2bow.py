from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from concrete.structure.ttypes import TokenLattice, TokenList, Token

import math


def load_lattice(input_path):
    with open(input_path, 'rb') as f:
        transportIn = TTransport.TFileObjectTransport(f)
        protocolIn = TBinaryProtocol.TBinaryProtocol(transportIn)
        lattice = TokenLattice()
        lattice.read(protocolIn)
        return lattice


def group_arcs_by_src(lattice):
    arcs_by_src = dict()
    if lattice.arcList is not None:
        for arc in lattice.arcList:
            if arc.src in arcs_by_src:
                arcs_by_src[arc.src].append(arc)
            else:
                arcs_by_src[arc.src] = [arc]
    return arcs_by_src


def extract_paths(arcs_by_src):
    paths = [[] for src in arcs_by_src]
    for i in xrange(len(arcs_by_src) - 1, -1, -1): # TODO edge cases?
        for arc in arcs_by_src[i]:
            if arc.dst in arcs_by_src:
                for (tail, weight) in paths[arc.dst]:
                    paths[arc.src].append(([arc] + tail, arc.weight + weight))
            else:
                paths[arc.src].append(([arc], arc.weight))

    if paths:
        return paths[0]
    else:
        return []


def compute_expected_counts(path_weight_pairs):
    normalizer = math.log(sum(math.exp(w) for (p, w) in path_weight_pairs))
    counts = dict()
    for (path, weight) in path_weight_pairs:
        p = math.exp(weight - normalizer)
        for arc in path:
            token = arc.token
            if token.text in counts:
                counts[token.text] += p
            else:
                counts[token.text] = p
    return counts


def compute_counts(path):
    counts = dict()
    for arc in path:
        token = arc.token
        if token.text in counts:
            counts[token.text] += 1
        else:
            counts[token.text] = 1
    return counts


def write_best_path(output_path, lattice, path):
    lattice.cachedBestPath = TokenList([Token(text=arc.token.text)
                                        for arc in path])
    with open(output_path, 'wb') as f:
        transport = TTransport.TFileObjectTransport(f)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        lattice.write(protocol)


def main():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.set_defaults(raw=False, best=False, write=False)
    parser.add_argument('input_path', type=str,
                        help='path to serialized concrete TokenLattice')
    parser.add_argument('--raw', action='store_true',
                        help='return all paths')
    parser.add_argument('--best', action='store_true',
                        help='return counts for best path')
    parser.add_argument('--write', action='store_true',
                        help='write back to lattice')
    args = parser.parse_args()

    lattice = load_lattice(args.input_path)
    arcs_by_src = group_arcs_by_src(lattice)
    path_weight_pairs = extract_paths(arcs_by_src)
    if args.raw:
        path_weight_pairs.sort(key=lambda pair: pair[1], reverse=True)
        for (path, weight) in path_weight_pairs:
            print (path, weight)
    else:
        if args.best:
            path = reduce(lambda p, q: (p[1] > q[1]) and p or q,
                          path_weight_pairs)
            if args.write:
                write_best_path(args.input_path, lattice, path[0])
            counts = compute_counts(path[0])
        else:
            counts = compute_expected_counts(path_weight_pairs)

        if not args.write:
            counts_items = counts.items()
            counts_items.sort(key=lambda pair: pair[1], reverse=True)
            for (w, p) in counts_items:
                print '%.9f %s' % (p, w)


if __name__ == '__main__':
    main()
