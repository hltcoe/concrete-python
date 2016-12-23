from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from concrete.structure.ttypes import TokenLattice, LatticePath


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


def find_best_path(arcs_by_src):
    subpath_weight_pairs = {0: ([], 0.)}  # indexed by dst
    farthest_reachable_dst = 0

    for i in xrange(len(arcs_by_src)):
        if i in subpath_weight_pairs:  # reachable
            (subpath, weight) = subpath_weight_pairs[i]
            for arc in arcs_by_src[i]:
                new_subpath = subpath + [arc]
                new_weight = arc.weight + weight
                new_pair = (new_subpath, new_weight)
                if arc.dst in subpath_weight_pairs:
                    if new_weight > subpath_weight_pairs[arc.dst][1]:
                        subpath_weight_pairs[arc.dst] = new_pair
                        farthest_reachable_dst = max(farthest_reachable_dst,
                                                     arc.dst)
                else:
                    subpath_weight_pairs[arc.dst] = new_pair
                    farthest_reachable_dst = max(farthest_reachable_dst,
                                                 arc.dst)

    return subpath_weight_pairs[farthest_reachable_dst]


def cache_best_path(output_path, lattice, path):
    lattice.cachedBestPath = LatticePath(tokenList=[arc.token for arc in path])
    with open(output_path, 'wb') as f:
        transport = TTransport.TFileObjectTransport(f)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        lattice.write(protocol)


def main():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.set_defaults(raw=False, best=False, cache_best=False)
    parser.add_argument('input_path', type=str,
                        help='path to serialized concrete TokenLattice')
    parser.add_argument('--best', action='store_true',
                        help='print best path')
    parser.add_argument('--cache_best', action='store_true',
                        help='cache best path to lattice')
    args = parser.parse_args()

    lattice = load_lattice(args.input_path)
    arcs_by_src = group_arcs_by_src(lattice)
    if args.best or args.cache_best:
        (path, weight) = find_best_path(arcs_by_src)
        if args.cache_best:
            cache_best_path(args.input_path, lattice, path)
        else:
            print ' '.join(arc.token.text for arc in path)


if __name__ == '__main__':
    main()
