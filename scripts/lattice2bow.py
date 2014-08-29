from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from concrete.structure.ttypes import TokenLattice

def load_lattice_best_path(path):
    with open(path, 'rb') as f:
        transportIn = TTransport.TFileObjectTransport(f)
        protocolIn = TBinaryProtocol.TBinaryProtocol(transportIn)
        lattice = TokenLattice()
        lattice.read(protocolIn)
        best_path = lattice.cachedBestPath
        if best_path is None:
            return None
        else:
            token_list = best_path.tokenList
            if token_list is None:
                return None
            else:
                return [t.text for t in token_list]
