#!/usr/bin/env python


"""
Deprecated: please use concrete-inspect.py instead.

Print human-readable information about a Communication to stdout

concrete_inspect.py is a command-line script for printing out information
about a Concrete Communication.
"""
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import codecs
import sys

import concrete.version
import concrete.inspect
from concrete.util import CommunicationReader, FileType


sys.stderr.write(
    'concrete_inspect.py is deprecated and will be removed in the future.\n')
sys.stderr.write('Please use concrete-inspect.py instead.\n')


def print_header(header):
    print()
    print(header)
    print('-' * len(header))


def print_header_if(header, condition):
    if condition:
        print_header(header)


def main():
    # Make stdout output UTF-8, preventing "'ascii' codec can't encode" errors
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)

    parser = argparse.ArgumentParser(
        description="Print information about a Concrete Communication to"
                    " stdout.  If communication_filename is specified, read"
                    " communication from file; otherwise, read from standard"
                    " input.",
    )
    parser.add_argument('--count', type=int,
                        help='Print at most this many communications.')
    parser.add_argument('--annotation-headers', action='store_true',
                        help='Print annotation type headers.')
    parser.add_argument("--char-offsets",
                        help="Print token text extracted from character offset"
                             "s (not the text stored in the tokenization) in '"
                             "ConLL-style' format",
                        action="store_true")
    parser.add_argument("--dependency",
                        help="Print HEAD and DEPREL tags for first dependency "
                             "parse in 'ConLL-style' format",
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
                        help="Print first set of lemma token tags in 'ConLL-st"
                             "yle' format",
                        action="store_true")
    parser.add_argument("--lemmas-tool",
                        type=str,
                        help='Filter --lemmas output to specified '
                             'tool (requires --lemmas)')
    parser.add_argument("--metadata",
                        help="Print metadata for tools used to annotate Commun"
                             "ication",
                        action="store_true")
    parser.add_argument("--metadata-tool",
                        type=str,
                        help='Filter --metadata output to specified '
                             'tool (requires --metadata)')
    parser.add_argument("--communication-taggings",
                        help="Print communication taggings",
                        action="store_true")
    parser.add_argument("--communication-taggings-tool",
                        type=str,
                        help='Filter --communication-taggings output to '
                             'specified tool (requires '
                             '--communication-taggings)')
    parser.add_argument("--mentions",
                        help="Print whitespace-separated tokens, with entity m"
                             "entions wrapped using <ENTITY ID=x> tags, where "
                             "'x' is the (zero-indexed) entity number",
                        action="store_true")
    parser.add_argument("--mentions-tool",
                        type=str,
                        help='Filter --mentions output to specified '
                             'tool (requires --mentions)')
    parser.add_argument("--ner",
                        help="Print first set of Named Entity Recognition toke"
                             "n tags in 'ConLL-style' format",
                        action="store_true")
    parser.add_argument("--ner-tool",
                        type=str,
                        help='Filter --ner output to specified '
                             'tool (requires --ner)')
    parser.add_argument("--pos",
                        help="Print first set of Part-Of-Speech token tags in "
                             "'ConLL-style' format",
                        action="store_true")
    parser.add_argument("--pos-tool",
                        type=str,
                        help='Filter --pos output to specified '
                             'tool (requires --pos)')
    parser.add_argument("--sections",
                        action='store_true',
                        help="Print text according to Section offsets"
                             "(textSpan values). These textSpans are assumed "
                             "to be valid.")
    parser.add_argument("--sections-tool",
                        type=str,
                        help='Filter --sections output to specified '
                             'tool (requires --sections)')
    parser.add_argument("--situation-mentions",
                        help="Print info about all SituationMentions",
                        action="store_true")
    parser.add_argument("--situation-mentions-tool",
                        type=str,
                        help='Filter --situation-mentions output to specified '
                             'tool (requires --situation-mentions)')
    parser.add_argument("--situations",
                        help="Print info about all Situations and their Situat"
                             "ionMentions",
                        action="store_true")
    parser.add_argument("--situations-tool",
                        type=str,
                        help='Filter --situations output to specified '
                             'tool (requires --situations)')
    parser.add_argument("--text",
                        help="Print .text field",
                        action="store_true")
    parser.add_argument("--text-tool",
                        type=str,
                        help='Filter --text output to specified '
                             'tool (requires --text)')
    parser.add_argument("--tokens",
                        help="Print whitespace-seperated tokens for *all* Toke"
                             "nizations in a Communication.  Each sentence tok"
                             "enization is printed on a separate line, and "
                             "empty lines indicate a section break",
                        action="store_true")
    parser.add_argument("--tokens-tool",
                        type=str,
                        help='Filter --tokens output to specified '
                             'tool (requires --tokens)')
    parser.add_argument("--treebank",
                        help="Print Penn-Treebank style parse trees for *all* "
                             "Constituent Parses in the Communication",
                        action="store_true")
    parser.add_argument("--treebank-tool",
                        type=str,
                        help='Filter --treebank output to specified '
                             'tool (requires --treebank)')
    parser.add_argument("--id",
                        help='Print communication id',
                        action='store_true')
    parser.add_argument("--id-tool",
                        type=str,
                        help='Filter --id output to specified '
                             'tool (requires --id)')
    parser.add_argument("--no-references",
                        help="Don't add references to communication (may preve"
                             "nt 'NoneType' errors)",
                        action="store_true")
    parser.add_argument('communication_filename',
                        nargs='?',
                        type=str,
                        help='Path to a Concrete Communication from which '
                        'to display information. If not specified, read '
                        'read from standard input')
    concrete.version.add_argparse_argument(parser)
    args = parser.parse_args()

    add_references = not args.no_references

    if args.communication_filename is not None:
        comms = CommunicationReader(args.communication_filename,
                                    add_references=add_references)
    else:
        comms = CommunicationReader('/dev/fd/0', add_references=add_references,
                                    filetype=FileType.STREAM)

    if not (args.char_offsets or args.dependency or args.lemmas or args.ner or
            args.pos or args.entities or args.mentions or args.metadata or
            args.sections or args.situation_mentions or args.situations or
            args.text or args.tokens or args.treebank or args.id or
            args.communication_taggings):
        parser.print_help()
        sys.exit(1)

    if ((args.dependency_tool and not args.dependency) or
            (args.lemmas_tool and not args.lemmas) or
            (args.ner_tool and not args.ner) or
            (args.pos_tool and not args.pos) or
            (args.entities_tool and not args.entities) or
            (args.mentions_tool and not args.mentions) or
            (args.metadata_tool and not args.metadata) or
            (args.sections_tool and not args.sections) or
            (args.situation_mentions_tool and not args.situation_mentions) or
            (args.situations_tool and not args.situations) or
            (args.text_tool and not args.text) or
            (args.tokens_tool and not args.tokens) or
            (args.treebank_tool and not args.treebank) or
            (args.id_tool and not args.id) or
            (args.communication_taggings_tool and
                not args.communication_taggings)):
        parser.print_help()
        sys.exit(1)

    comm_num = 0

    for (comm, _) in comms:
        if args.count is not None and comm_num == args.count:
            break

        if args.id:
            print_header_if('id', args.annotation_headers)
            concrete.inspect.print_id_for_communication(
                comm, tool=args.id_tool)
        if args.text:
            print_header_if('text', args.annotation_headers)
            concrete.inspect.print_text_for_communication(
                comm, tool=args.text_tool)
        if args.sections:
            print_header_if('sections', args.annotation_headers)
            concrete.inspect.print_sections(comm, tool=args.sections_tool)
        if args.tokens:
            print_header_if('tokens', args.annotation_headers)
            concrete.inspect.print_tokens_for_communication(
                comm, tool=args.tokens_tool)
        if args.treebank:
            print_header_if('treebank', args.annotation_headers)
            concrete.inspect.print_penn_treebank_for_communication(
                comm, tool=args.treebank_tool)
        if (args.char_offsets or args.dependency or args.lemmas or args.ner or
                args.pos):
            print_header_if('conll', args.annotation_headers)
            concrete.inspect.print_conll_style_tags_for_communication(
                comm, char_offsets=args.char_offsets,
                dependency=args.dependency,
                lemmas=args.lemmas, ner=args.ner, pos=args.pos,
                dependency_tool=args.dependency_tool,
                lemmas_tool=args.lemmas_tool,
                pos_tool=args.pos_tool,
                ner_tool=args.ner_tool)
        if args.entities:
            print_header_if('entities', args.annotation_headers)
            concrete.inspect.print_entities(comm, tool=args.entities_tool)
        if args.mentions:
            print_header_if('mentions', args.annotation_headers)
            concrete.inspect.print_tokens_with_entityMentions(
                comm, tool=args.mentions_tool)
        if args.situations:
            print_header_if('situations', args.annotation_headers)
            concrete.inspect.print_situations(comm, tool=args.situations_tool)
        if args.situation_mentions:
            print_header_if('situation mentions', args.annotation_headers)
            concrete.inspect.print_situation_mentions(
                comm, tool=args.situation_mentions_tool)
        if args.communication_taggings:
            print_header_if('communication taggings', args.annotation_headers)
            concrete.inspect.print_communication_taggings_for_communication(
                comm, tool=args.communication_taggings_tool)
        if args.metadata:
            print_header_if('metadata', args.annotation_headers)
            concrete.inspect.print_metadata(comm, tool=args.metadata_tool)

        comm_num += 1


if __name__ == "__main__":
    main()
