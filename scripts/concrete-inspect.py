#!/usr/bin/env python

"""Print human-readable information about a Communication to stdout

concrete_inspect.py is a command-line script for printing out information
about a Concrete Communication.
"""
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import json
import sys

import concrete.version
import concrete.inspect
from concrete.util import (
    CommunicationReader, FileType, set_stdout_encoding,
    filter_annotations_json, lun
)


BASE_ANNOTATION_TYPES = (
    'id',
    'text',
    'sections',
    'entities',
    'mentions',
    'situations',
    'situation-mentions',
    'communication-taggings',
    'metadata',
    'treebank',
    'tokens',
    'dependency',
    'lemmas',
    'ner',
    'pos',
)


def print_header(header):
    print()
    print(header)
    print('-' * len(header))


def print_header_if(header, condition):
    if condition:
        print_header(header)


def main():
    set_stdout_encoding()

    parser = argparse.ArgumentParser(
        description='''
Print information about a Concrete Communication to stdout.  If
communication_filename is specified, read communication from file;
otherwise, read from standard input.  One or more annotation flags must
be specified (calling this script with no arguments is an error).''',
        epilog='''
Filtering annotations:

    TYPE
        Should be one of the following:

            {}
            other-tag:TAG-TYPE

        (with TAG-TYPE replaced by a token tagging type given to the
        --other-tags flag).

    FILTER_ANNOTATIONS_JSON
        Can be for example

            {}

        to print annotations by the Goldenhorse tool or

            {}

        to print only the most recent annotation.

        Annotations of the specified type are filtered by parsing
        FILTER_ANNOTATIONS_JSON and passing the results as keyword
        arguments to concrete.util.metadata.filter_annotations, which
        has the following documentation at the time of writing (see
        the API documentation for updates):

        filter_fields (dict): dict of fields and their desired values
            by which to filter annotations (keep annotations whose
            field FIELD equals VALUE for all FIELD: VALUE entries).
            Default: keep all annotations.  Valid fields are:
            tool, timestamp, kBest.
        sort_field (str): field by which to re-order annotations.
            Default: do not re-order annotations.
        sort_reverse (bool): True to reverse order of annotations
            (after sorting, if any).
        action_if_multiple (str): action to take if, after filtering,
            there is more than one annotation left.  'pass' to
            return all filtered and re-ordered annotations, 'raise' to
            raise an exception of type MultipleAnnotationsError,
            'first' to return a list containing the first annotation
            after filtering and re-ordering, or 'last' to return a list
            containing the last annotation after filtering and
            re-ordering.
        action_if_zero (str): action to take if, after filtering, there
            are no annotations left.  'pass' to return an empty list,
            'raise' to raise an exception of type ZeroAnnotationsError.

        The default behavior is to do no filtering (or re-ordering).
        '''.format(
            '\n            '.join(BASE_ANNOTATION_TYPES),
            json.dumps(dict(filter_fields=dict(tool='Goldenhorse'))),
            json.dumps(dict(action_if_multiple='last', sort_field='timestamp')),
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--count', type=int,
                        help='Print at most this many communications.')
    parser.add_argument('--annotation-headers', action='store_true',
                        help='Print a header above each annotation '
                             '(useful if multiple annotation flags are '
                             'specified and it\'s not clear where the output '
                             'of one annotation ends and the output of the '
                             'next annotation begins)')
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
    parser.add_argument("--metadata",
                        help="Print metadata for tools used to annotate Commun"
                             "ication",
                        action="store_true")
    parser.add_argument("--communication-taggings",
                        help="Print communication taggings",
                        action="store_true")
    parser.add_argument("--mentions",
                        help="Print whitespace-separated tokens, with entity m"
                             "entions wrapped using <ENTITY ID=x> tags, where "
                             "'x' is the (zero-indexed) entity number",
                        action="store_true")
    parser.add_argument("--ner",
                        help="Print first set of Named Entity Recognition toke"
                             "n tags in 'CoNLL-style' format",
                        action="store_true")
    parser.add_argument("--pos",
                        help="Print first set of Part-Of-Speech token tags in "
                             "'CoNLL-style' format",
                        action="store_true")
    parser.add_argument("--sections",
                        action='store_true',
                        help="Print text according to Section offsets"
                             "(textSpan values). These textSpans are assumed "
                             "to be valid.")
    parser.add_argument("--situation-mentions",
                        help="Print info about all SituationMentions",
                        action="store_true")
    parser.add_argument("--situations",
                        help="Print info about all Situations and their Situat"
                             "ionMentions",
                        action="store_true")
    parser.add_argument("--other-tag",
                        metavar='TAG-TYPE',
                        help="Tagging type of other token tagging to display "
                             "(this flag can be specified multiple times to "
                             "display multiple other token taggings)",
                        action='append')
    parser.add_argument("--text",
                        help="Print .text field",
                        action="store_true")
    parser.add_argument("--tokens",
                        help="Print whitespace-seperated tokens for *all* Toke"
                             "nizations in a Communication.  Each sentence tok"
                             "enization is printed on a separate line, and "
                             "empty lines indicate a section break",
                        action="store_true")
    parser.add_argument("--treebank",
                        help="Print Penn-Treebank style parse trees for *all* "
                             "Constituent Parses in the Communication",
                        action="store_true")
    parser.add_argument("--id",
                        help='Print communication id',
                        action='store_true')
    parser.add_argument('--filter-annotations',
                        nargs=2,
                        metavar=('TYPE', 'FILTER_ANNOTATIONS_JSON'),
                        help='Filter (and/or re-order) annotations of '
                             'specified type TYPE according to '
                             'FILTER_ANNOTATIONS_JSON (a string containing '
                             'json-encoded arguments to the '
                             'filter_annotations function).  '
                             'See below for details.',
                        action='append')
    parser.add_argument("--no-references",
                        help="Don't add references to communication while "
                             "loading (may prevent some 'NoneType' errors but "
                             "is incompatible with some annotations)",
                        action="store_true")
    parser.add_argument("--dependency-tool",
                        type=str,
                        help='Deprecated:  Filter --dependency output by tool.')
    parser.add_argument("--entities-tool",
                        type=str,
                        help='Deprecated:  Filter --entities output by tool.')
    parser.add_argument("--lemmas-tool",
                        type=str,
                        help='Deprecated:  Filter --lemmas output by tool.')
    parser.add_argument("--metadata-tool",
                        type=str,
                        help='Deprecated:  Filter --metadata output by tool.')
    parser.add_argument("--communication-taggings-tool",
                        type=str,
                        help='Deprecated:  Filter --communication-taggings output by tool.')
    parser.add_argument("--mentions-tool",
                        type=str,
                        help='Deprecated:  Filter --mentions output by tool.')
    parser.add_argument("--ner-tool",
                        type=str,
                        help='Deprecated:  Filter --ner output by tool.')
    parser.add_argument("--pos-tool",
                        type=str,
                        help='Deprecated:  Filter --pos output by tool.')
    parser.add_argument("--sections-tool",
                        type=str,
                        help='Deprecated:  Filter --sections output by tool.')
    parser.add_argument("--situation-mentions-tool",
                        type=str,
                        help='Deprecated:  Filter --situation-mentions output by tool.')
    parser.add_argument("--situations-tool",
                        type=str,
                        help='Deprecated:  Filter --situations output by tool.')
    parser.add_argument("--text-tool",
                        type=str,
                        help='Deprecated:  Filter --text output by tool.')
    parser.add_argument("--tokens-tool",
                        type=str,
                        help='Deprecated:  Filter --tokens output by tool.')
    parser.add_argument("--treebank-tool",
                        type=str,
                        help='Deprecated:  Filter --treebank output by tool.')
    parser.add_argument("--id-tool",
                        type=str,
                        help='Deprecated:  Filter --id output by tool.')
    parser.add_argument('communication_filename',
                        nargs='?',
                        type=str,
                        help='Path to a Concrete Communication from which '
                        'to display information. If not specified, read '
                        'from standard input')
    concrete.version.add_argparse_argument(parser)
    args = parser.parse_args()

    add_references = not args.no_references

    # if communication_filename is None, read from stdin
    if args.communication_filename is not None:
        comms = CommunicationReader(args.communication_filename,
                                    add_references=add_references)
    else:
        comms = CommunicationReader('/dev/fd/0', add_references=add_references,
                                    filetype=FileType.STREAM)

    # check that an annotation argument was specified
    if not (args.char_offsets or args.dependency or args.lemmas or args.ner or
            args.pos or args.entities or args.mentions or args.metadata or
            args.sections or args.situation_mentions or args.situations or
            args.text or args.tokens or args.treebank or args.id or
            args.communication_taggings or args.other_tag):
        parser.print_help()
        sys.exit(1)

    # show deprecation warnings for --x-tool
    if (args.dependency_tool or
            args.lemmas_tool or
            args.ner_tool or
            args.pos_tool or
            args.entities_tool or
            args.mentions_tool or
            args.metadata_tool or
            args.sections_tool or
            args.situation_mentions_tool or
            args.situations_tool or
            args.text_tool or
            args.tokens_tool or
            args.treebank_tool or
            args.id_tool or
            args.communication_taggings_tool):
        if args.filter_annotations:
            parser.print_help()
            sys.exit(1)
        else:
            logging.warning(
                '--*-tool is deprecated; please use --filter-annotations '
                'instead')

    # check that --x-tool was not specified without --x
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

    # facilitate construction of filter functions from args
    filters_by_annotation_type = dict(lun(args.filter_annotations))

    def _get_annotation_filter(annotation_type):
        '''
        Return filter function for given annotation type, or None.
        '''
        if annotation_type in filters_by_annotation_type:
            return lambda annotations: filter_annotations_json(
                annotations, filters_by_annotation_type[annotation_type]
            )
        else:
            return None

    # loop over communications and print annotations
    comm_num = 0

    for (comm, _) in comms:
        if args.count is not None and comm_num == args.count:
            break

        if args.id:
            print_header_if('id', args.annotation_headers)
            concrete.inspect.print_id_for_communication(
                comm, tool=args.id_tool,
                communication_filter=_get_annotation_filter('id'))
        if args.text:
            print_header_if('text', args.annotation_headers)
            concrete.inspect.print_text_for_communication(
                comm, tool=args.text_tool,
                communication_filter=_get_annotation_filter('text'))
        if args.sections:
            print_header_if('sections', args.annotation_headers)
            concrete.inspect.print_sections(
                comm, tool=args.sections_tool,
                communication_filter=_get_annotation_filter('sections'))
        if args.tokens:
            print_header_if('tokens', args.annotation_headers)
            concrete.inspect.print_tokens_for_communication(
                comm, tool=args.tokens_tool,
                tokenization_filter=_get_annotation_filter('tokens'))
        if args.treebank:
            print_header_if('treebank', args.annotation_headers)
            concrete.inspect.print_penn_treebank_for_communication(
                comm, tool=args.treebank_tool,
                parse_filter=_get_annotation_filter('treebank'))
        if (args.char_offsets or args.dependency or args.lemmas or args.ner or
                args.pos or args.other_tag):
            print_header_if('conll', args.annotation_headers)
            concrete.inspect.print_conll_style_tags_for_communication(
                comm, char_offsets=args.char_offsets,
                dependency=args.dependency,
                lemmas=args.lemmas, ner=args.ner, pos=args.pos,
                other_tags=dict(
                    (t, _get_annotation_filter('other-tag:' + t))
                    for t in lun(args.other_tag)
                ),
                dependency_tool=args.dependency_tool,
                dependency_parse_filter=_get_annotation_filter('dependency'),
                lemmas_tool=args.lemmas_tool,
                lemmas_filter=_get_annotation_filter('lemmas'),
                pos_tool=args.pos_tool,
                pos_filter=_get_annotation_filter('pos'),
                ner_tool=args.ner_tool,
                ner_filter=_get_annotation_filter('ner'))
        if args.entities:
            print_header_if('entities', args.annotation_headers)
            concrete.inspect.print_entities(
                comm, tool=args.entities_tool,
                entity_set_filter=_get_annotation_filter('entities'))
        if args.mentions:
            print_header_if('mentions', args.annotation_headers)
            concrete.inspect.print_tokens_with_entityMentions(
                comm, tool=args.mentions_tool,
                entity_mention_set_filter=_get_annotation_filter('mentions'))
        if args.situations:
            print_header_if('situations', args.annotation_headers)
            concrete.inspect.print_situations(
                comm, tool=args.situations_tool,
                situation_set_filter=_get_annotation_filter('situations'))
        if args.situation_mentions:
            print_header_if('situation mentions', args.annotation_headers)
            concrete.inspect.print_situation_mentions(
                comm, tool=args.situation_mentions_tool,
                situation_mention_set_filter=_get_annotation_filter(
                    'situation-mentions'))
        if args.communication_taggings:
            print_header_if('communication taggings', args.annotation_headers)
            concrete.inspect.print_communication_taggings_for_communication(
                comm, tool=args.communication_taggings_tool,
                communication_tagging_filter=_get_annotation_filter(
                    'communication-taggings'))
        if args.metadata:
            print_header_if('metadata', args.annotation_headers)
            concrete.inspect.print_metadata(
                comm, tool=args.metadata_tool,
                annotation_filter=_get_annotation_filter('metadata'))

        comm_num += 1


if __name__ == "__main__":
    main()
