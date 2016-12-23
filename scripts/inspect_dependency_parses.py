#!/usr/bin/env python

"""
Command line script to (partially) validate a Concrete Communication

This script is a thin wrapper around the functionality in the
concrete.validate library.
"""

import argparse
import logging

import networkx as nx

from concrete.util.tokenization import get_comm_tokenizations
import concrete.version
from concrete.util.file_io import CommunicationReader, FileType


def main():
    parser = argparse.ArgumentParser(
        description="Check dependency parse graph for errors")
    parser.add_argument('communication_file',
                        nargs='?',
                        type=str,
                        help='file to read communications from '
                             '(if not specified, read from standard input)')
    concrete.version.add_argparse_argument(parser)
    args = parser.parse_args()

    # Won't work on Windows... but that use case is very unlikely
    if args.communication_file is None:
        reader_kwargs = dict(filetype=FileType.STREAM)
        input_path = '/dev/fd/0'
    else:
        reader_kwargs = dict()
        input_path = args.communication_file

    logging.basicConfig(
        format='%(levelname)7s:  %(message)s', level=logging.INFO)

    for (comm, filename) in CommunicationReader(input_path, **reader_kwargs):
        logging.info(u"Inspecting Communication with ID '%s" % comm.id)
        for tokenization in get_comm_tokenizations(comm):
            inspect_dependency_parses(tokenization)


def inspect_dependency_parses(tokenization):

    def _get_token_text(tokenization):
        return " ".join([t.text for t in tokenization.tokenList.tokenList])

    if tokenization.dependencyParseList:
        total_tokens = len(tokenization.tokenList.tokenList)
        for dependencyParse in tokenization.dependencyParseList:
            dependency_parse_tree = nx.DiGraph()

            # Add nodes to dependency parse tree
            for dependency in dependencyParse.dependencyList:
                if (dependency.gov is None and
                        dependency.edgeType.lower() != "root"):
                    logging.error((u"  Found a null dependency parse node with"
                                   u" governer whose edgeType is '%s' instead"
                                   u" of 'root'") % dependency.edgeType)
                if dependency.gov is not None:
                    if dependency.gov < -1 or dependency.gov > total_tokens:
                        logging.error(u"  Found a null dependency parse node"
                                      u" with invalid governer of '%d'" %
                                      dependency.gov)
                    dependency_parse_tree.add_node(dependency.gov)
                dependency_parse_tree.add_node(dependency.dep)

            # Add edges to dependency parse tree
            for dependency in dependencyParse.dependencyList:
                if dependency.gov is not None:
                    dependency_parse_tree.add_edge(
                        dependency.gov, dependency.dep)

            # Check if dependency parse "tree" is a fully connected graph
            undirected_graph = dependency_parse_tree.to_undirected()
            try:
                if not nx.is_connected(undirected_graph):
                    logging.error((u"  The dependency parse graph created by"
                                   u" '%s' is not a fully connected graph -"
                                   u" the graph has %d components. Token text:"
                                   u" '%s'") %
                                  (dependencyParse.metadata.tool,
                                   nx.number_connected_components(
                                       undirected_graph),
                                   _get_token_text(tokenization)))
            except nx.exception.NetworkXPointlessConcept:
                logging.warning((u"  The dependency parse graph created by"
                                 u" '%s' does not have any nodes. Token text:"
                                 u" '%s'") %
                                (dependencyParse.metadata.tool,
                                 _get_token_text(tokenization)))


if __name__ == "__main__":
    main()
