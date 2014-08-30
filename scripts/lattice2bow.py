from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from concrete.structure.ttypes import TokenLattice


def load_lattice(path):
    with open(path, 'rb') as f:
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


def compute_expected_counts(arcs_by_src):
    counts = dict()
    for (src, arcs) in arcs_by_src.items():
        normalizer = float(sum(pow(10., arc.weight) for arc in arcs))
        for arc in arcs:
            token = arc.token
            prob = pow(10., arc.weight) / normalizer
            if token.text in counts:
                counts[token.text] += prob
            else:
                counts[token.text] = prob
    return counts


def sort_paths(paths):
    paths.sort(key=lambda pair: pair[1], reverse=True)


def main():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.set_defaults(all=False)
    parser.add_argument('input_path', type=str,
                        help='path to serialized concrete TokenLattice')
    parser.add_argument('--all', action='store_true',
                        help='return all paths')
    args = parser.parse_args()

    lattice = load_lattice(args.input_path)
    arcs_by_src = group_arcs_by_src(lattice)
    if args.all:
        paths = extract_paths(arcs_by_src)
        sort_paths(paths)
        for (path, weight) in paths:
            print (path, weight)
    else:
        print compute_expected_counts(arcs_by_src)


if __name__ == '__main__':
    main()
