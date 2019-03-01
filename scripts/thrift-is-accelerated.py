#!/usr/bin/env python

import sys

from thrift.transport import TTransport
from thrift.protocol import TCompactProtocol

try:
    transport = TTransport.TMemoryBuffer()
    TCompactProtocol.TCompactProtocolAccelerated(transport, fallback=False)
    sys.stderr.write('Thrift is accelerated\n')
    sys.exit(0)
except Exception:
    sys.stderr.write('ERROR: Thrift is NOT accelerated\n')
    sys.exit(-1)
