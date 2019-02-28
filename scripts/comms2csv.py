#!/usr/bin/env python

import argparse

from thrift import TSerialization
from thrift.protocol import TJSONProtocol
import unicodecsv

from concrete.util import CommunicationReader


def main():
    parser = argparse.ArgumentParser(
        description="Encode a Communication archive as a CSV file, where each row contains a "
        "TJSONProtocol encoded Communication",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('comms_archive',
                        help="A directory, TGZ file or Zip file of Communications")
    parser.add_argument('csv_file',
                        help="Output CSV file with TJSONProtocol encoded Communications")
    parser.add_argument('--column-name', default='comm',
                        help="Name to use for CSV column header")
    args = parser.parse_args()

    csv_fh = open(args.csv_file, 'wb')

    fieldnames = [args.column_name]
    writer = unicodecsv.DictWriter(csv_fh, fieldnames, lineterminator='\n',
                                   quoting=unicodecsv.QUOTE_ALL)
    writer.writeheader()

    for (comm, filename) in CommunicationReader(args.comms_archive):
        json_communication = TSerialization.serialize(
            comm, TJSONProtocol.TJSONProtocolFactory()).decode('utf-8')
        writer.writerow({args.column_name: json_communication})


if __name__ == "__main__":
    main()
