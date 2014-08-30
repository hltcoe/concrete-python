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


def extract_best_path(lattice):
    best_path = lattice.cachedBestPath
    if best_path is None:
        return None
    else:
        token_list = best_path.tokenList
        if token_list is None:
            return None
        else:
            return [t.text for t in token_list]


def extract_paths(lattice):
    arcs = dict()
    if lattice.arcList is not None:
        for arc in lattice.arcList:
            if arc.src in arcs:
                arcs[arc.src].append(arc)
            else:
                arcs[arc.src] = [arc]

    paths = dict((i, []) for i in xrange(len(arcs)))
    for i in xrange(len(arcs) - 1, -1, -1):
        for arc in arcs[i]:
            if arc.dst < len(arcs):
                for (tail, weight) in paths[arc.dst]:
                    paths[arc.src].append(([arc] + tail, arc.weight + weight))
            else:
                paths[arc.src].append(([arc], arc.weight))

    if paths:
        return paths[0]
    else:
        return []


def main():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.set_defaults(best=False)
    parser.add_argument('input_path', type=str,
                        help='path to serialized concrete TokenLattice')
    parser.add_argument('--best', action='store_true',
                        help='return counts for best path')
    args = parser.parse_args()

    lattice = load_lattice(args.input_path)
    if args.best:
        print extract_best_path(lattice)
    else:
        print dir(lattice)


if __name__ == '__main__':
    main()
