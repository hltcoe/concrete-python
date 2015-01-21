#!/usr/bin/env python

"""
"""

import unittest

from concrete import AnnotationMetadata, Communication
import concrete.inspect
from concrete.util import generate_UUID
from concrete.validate import validate_communication

from test_validate_communication import read_test_comm


class TestConcreteInspect(unittest.TestCase):
    def setUp(self):
        self.comm = read_test_comm()

    def test_print_conll_style_tags_for_communication(self):
        concrete.inspect.print_conll_style_tags_for_communication(
            self.comm, char_offsets=True, dependency=True, lemmas=True, ner=True, pos=True)

    def test_print_entities(self):
        concrete.inspect.print_entities(self.comm)

    def test_print_situation_mentions(self):
        concrete.inspect.print_situation_mentions(self.comm)

    def test_print_situations(self):
        concrete.inspect.print_situations(self.comm)

    def test_print_text_for_communication(self):
        concrete.inspect.print_text_for_communication(self.comm)

    def test_print_tokens_with_entityMentions(self):
        concrete.inspect.print_tokens_with_entityMentions(self.comm)

    def test_print_tokens_for_communication(self):
        concrete.inspect.print_tokens_for_communication(self.comm)

    def test_print_penn_treebank_for_communication(self):
        concrete.inspect.print_penn_treebank_for_communication(self.comm)


if __name__ == '__main__':
    unittest.main(buffer=True)
