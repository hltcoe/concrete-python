from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.protocol import TCompactProtocol
from thrift import Thrift

from concrete.services import Annotator

try:
    transport = TSocket.TSocket('localhost', 33221)
    transport = TTransport.TFramedTransport(transport)
    protocol = TCompactProtocol.TCompactProtocol(transport)

    cli = Annotator.Client(protocol)
    transport.open()
    res = cli.annotate(comm)
    transport.close()
    print res

except Thrift.TException, tx:
    print "Got an error: %s : perhaps the server isn't running there?" % (tx.message)
