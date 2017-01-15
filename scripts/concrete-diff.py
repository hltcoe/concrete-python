#!/usr/bin/env python

"""
Compare two Concrete files by converting to JSON then running the Git
diff command
"""

import concrete.version
import argparse
import codecs
import os
import os.path
import subprocess
import tempfile

from concrete.util import communication_file_to_json


def main():
    parser = argparse.ArgumentParser(
        description="Compare JSON representation of two concrete files")
    parser.add_argument('--include-uuids', action='store_true',
                        help="Include UUIDs in JSON output")
    parser.add_argument('--include-timestamps', action='store_true',
                        help="Include timestamps in JSON output")
    parser.add_argument('file_one')
    parser.add_argument('file_two')
    concrete.version.add_argparse_argument(parser)
    args = parser.parse_args()

    tmp_path = tempfile.mkdtemp()

    json_one_filename = os.path.join(tmp_path, os.path.basename(args.file_one))
    json_two_filename = os.path.join(tmp_path, os.path.basename(args.file_two))

    # Prevent filename collision
    if json_one_filename == json_two_filename:
        json_two_filename += ".1"

    json_comm_one = communication_file_to_json(
        args.file_one, remove_timestamps=not args.include_timestamps,
        remove_uuids=not args.include_uuids)
    json_comm_two = communication_file_to_json(
        args.file_two, remove_timestamps=not args.include_timestamps,
        remove_uuids=not args.include_uuids)

    codecs.open(json_one_filename, "w", encoding="utf-8").write(json_comm_one)
    codecs.open(json_two_filename, "w", encoding="utf-8").write(json_comm_two)

    diff_command = "diff --unified %s %s" % (
        json_one_filename, json_two_filename)
    diff_output = subprocess.Popen(
        diff_command, shell=True, stdout=subprocess.PIPE).stdout.read()

    # Clean up temporary files
    os.remove(json_one_filename)
    os.remove(json_two_filename)
    os.rmdir(tmp_path)

    print diff_output


if __name__ == "__main__":
    main()
