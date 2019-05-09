#!/usr/bin/env python

import argparse

from thrift import TSerialization
from thrift.protocol import TJSONProtocol
import unicodecsv

from concrete import Communication
from concrete.util import CommunicationWriterZip


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_file')
    parser.add_argument('comms_zip_file')
    parser.add_argument('--comm-field', default='Answer.modified_comm')
    args = parser.parse_args()

    csv_fh = open(args.csv_file, 'rb')
    reader = unicodecsv.DictReader(csv_fh)

    with CommunicationWriterZip(args.comms_zip_file) as writer:
        for row in reader:
            json_comm = row[args.comm_field]
            comm = Communication()
            TSerialization.deserialize(
                comm, json_comm.encode('utf-8'),
                protocol_factory=TJSONProtocol.TJSONProtocolFactory())
            writer.write(comm, comm.id + '.comm')


if __name__ == "__main__":
    main()
