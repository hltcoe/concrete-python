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
        description="Print information about a Concrete Communication to "
                    "stdout in CoNLL format.  If communication_filename is "
                    "specified, read communication from file; otherwise, read "
                    "from standard input."
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
    parser.add_argument("--dependency-tool",
                        type=str,
                        help='Filter --dependency output to specified '
                             'tool (requires --dependency)')
    parser.add_argument("--entities",
                        help="Print info about all Entities and their EntityMe"
                             "ntions",
                        action="store_true")
    parser.add_argument("--entities-tool",
                        type=str,
                        help='Filter --entities output to specified '
                             'tool (requires --entities)')
    parser.add_argument("--lemmas",
                        help="Print first set of lemma token tags in 'CoNLL-st"
                             "yle' format",
                        action="store_true")
    parser.add_argument("--lemmas-tool",
                        type=str,
                        help='Filter --lemmas output to specified '
                             'tool (requires --lemmas)')
    parser.add_argument("--ner",
                        help="Print first set of Named Entity Recognition toke"
                             "n tags in 'CoNLL-style' format",
                        action="store_true")
    parser.add_argument("--ner-tool",
                        type=str,
                        help='Filter --ner output to specified '
                             'tool (requires --ner)')
    parser.add_argument("--pos",
                        help="Print first set of Part-Of-Speech token tags in "
                             "'CoNLL-style' format",
                        action="store_true")
    parser.add_argument("--pos-tool",
                        type=str,
                        help='Filter --pos output to specified '
                             'tool (requires --pos)')
    parser.add_argument("--other-tag",
                        help="Tagging type of other token tagging to display "
                             "(this flag can be specified multiple times to "
                             "display multiple other token taggings)",
                        action='append')
    parser.add_argument('communication_filename',
                        nargs='?',
                        type=str,
                        help='Path to a Concrete Communication from which '
                        'to display information. If not specified, read '
                        'from standard input')
    concrete.version.add_argparse_argument(parser)
    args = parser.parse_args()

    if args.communication_filename is not None:
        comms = CommunicationReader(args.communication_filename,
                                    add_references=False)
    else:
        comms = CommunicationReader('/dev/fd/0', add_references=False,
                                    filetype=FileType.STREAM)

    if ((args.dependency_tool and not args.dependency) or
            (args.lemmas_tool and not args.lemmas) or
            (args.ner_tool and not args.ner) or
            (args.pos_tool and not args.pos) or
            (args.entities_tool and not args.entities)):
        parser.print_help()
        sys.exit(1)

    comm_num = 0

    for (comm, _) in comms:
        if args.count is not None and comm_num == args.count:
            break

        concrete.inspect.print_conll_style_tags_for_communication(
            comm, char_offsets=args.char_offsets,
            dependency=args.dependency,
            lemmas=args.lemmas, ner=args.ner, pos=args.pos,
            other_tags=args.other_tag,
            dependency_tool=args.dependency_tool,
            lemmas_tool=args.lemmas_tool,
            pos_tool=args.pos_tool,
            ner_tool=args.ner_tool)

        comm_num += 1


if __name__ == "__main__":
    main()
