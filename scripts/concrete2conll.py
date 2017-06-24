#!/usr/bin/env python

"""Print CoNLL format of a Communication to stdout

concrete_inspect.py is a command-line script for printing out information
about a Concrete Communication.
"""
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import sys

import concrete.version
import concrete.inspect
from concrete.util import CommunicationReader, FileType
from concrete.util import set_stdout_encoding


def main():
    set_stdout_encoding()

    parser = argparse.ArgumentParser(
        description="Print information about one or more Concrete "
                    "Communications to stdout in CoNLL format.  "
                    "Suitable for programmatic use (use as input to another "
                    "program).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--count', type=int,
                        help='Print at most this many communications.')
    parser.add_argument("--char-offsets",
                        help="Print token text extracted from character offset"
                             "s (not the text stored in the tokenization) in '"
                             "CoNLL-style' format",
                        action="store_true")
    parser.add_argument("--dependency",
                        help="Print HEAD and DEPREL tags for first dependency "
                             "parse in 'CoNLL-style' format",
                        action="store_true")
    parser.add_argument("--entities",
                        help="Print info about all Entities and their EntityMe"
                             "ntions",
                        action="store_true")
    parser.add_argument("--lemmas",
                        help="Print first set of lemma token tags in 'CoNLL-st"
                             "yle' format",
                        action="store_true")
    parser.add_argument("--ner",
                        help="Print first set of Named Entity Recognition toke"
                             "n tags in 'CoNLL-style' format",
                        action="store_true")
    parser.add_argument("--pos",
                        help="Print first set of Part-Of-Speech token tags in "
                             "'CoNLL-style' format",
                        action="store_true")
    parser.add_argument("--other-tag",
                        help="Tagging type of other token tagging to display "
                             "(this flag can be specified multiple times to "
                             "display multiple other token taggings)",
                        action='append')
    parser.add_argument('--filter-annotations',
                        nargs=2,
                        metavar=('TYPE', 'FILTER_ANNOTATIONS_JSON'),
                        help='Type of annotation to filter and string '
                             'representing second argument to '
                             'filter_annotations_json.  TYPE should be one of '
                             'char-offsets, dependency, entities, lemmas, '
                             'ner, pos, or other-tag:TAG-NAME (with TAG-TYPE '
                             'replaced by the desired other token tagging '
                             'type')
                        action='append')
    parser.add_argument('--annotation-allow-multi',
                        help='print multiple columns of the same annotation',
                        action='store_true')
    parser.add_argument('communication_filename',
                        help='Path to a Concrete Communication from which '
                        'to display information, or - for standard input')
    concrete.version.add_argparse_argument(parser)
    args = parser.parse_args()

    if args.communication_filename != '-':
        comms = CommunicationReader(args.communication_filename,
                                    add_references=False)
    else:
        comms = CommunicationReader('/dev/fd/0', add_references=False,
                                    filetype=FileType.STREAM)

    comm_num = 0

    for (comm, _) in comms:
        if args.count is not None and comm_num == args.count:
            break

        concrete.inspect.print_conll_style_tags_for_communication(
            comm, char_offsets=args.char_offsets,
            dependency=args.dependency,
            lemmas=args.lemmas, ner=args.ner, pos=args.pos,
            other_tags=args.other_tag)

        comm_num += 1


if __name__ == "__main__":
    main()
