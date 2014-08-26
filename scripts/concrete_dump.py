#!/usr/bin/env python

"""Utility to dump 
"""

import argparse

import concrete.util


def main():
    parser = argparse.ArgumentParser(description="Print information about a Concrete Communication to stdout")
    parser.add_argument("--treebank", help="Print Penn-Treebank style parse trees",
                        action="store_true")
    parser.add_argument("communication_file")
    args = parser.parse_args()

    comm = concrete.util.read_communication_from_file(args.communication_file)

    if args.treebank:
        print_penn_treebank_for_communication(comm)


def print_penn_treebank_for_communication(comm):
    """Print Penn-Treebank parse trees for all tokenizations

    Args:
        comm: A Concrete Communication object
    """
    tokenizations = get_tokenizations_in_communication(comm)

    for tokenization in tokenizations:
        if tokenization.parse:
            print penn_treebank_for_parse(tokenization.parse) + "\n\n"


def penn_treebank_for_parse(parse):
    """Get a Penn-Treebank style string for a Concrete Parse object

    Args:
        parse: A Concrete Parse object

    Returns:
        A string containing a Penn Treebank style parse tree representation
    """
    def _traverse_parse(nodes, node_index, indent=0):
        s = ""
        indent += len(nodes[node_index].tag) + 2
        if nodes[node_index].childList:
            s += "(%s " % nodes[node_index].tag
            for i, node_index in enumerate(nodes[node_index].childList):
                if i > 0:
                    s += "\n" + " "*indent
                s += _traverse_parse(nodes, node_index, indent)
            s += ")"
        else:
            s += nodes[node_index].tag
        return s

    return _traverse_parse(parse.constituentList, 0)


def get_tokenizations_in_communication(comm):
    """Returns a flat list of all Tokenization objects in a Communication

    Args:
        comm: A Concrete Communication

    Returns:
        A list of all Tokenization objects within the Communication
    """
    tokenizations = []

    if comm.sectionSegmentations:
        for sectionSegmentation in comm.sectionSegmentations:
            for section in sectionSegmentation.sectionList:
                if section.sentenceSegmentation:
                    for sentenceSegmentation in section.sentenceSegmentation:
                        for sentence in sentenceSegmentation.sentenceList:
                            for tokenization in sentence.tokenizationList:
                                tokenizations.append(tokenization)
    return tokenizations


if __name__ == "__main__":
    main()
