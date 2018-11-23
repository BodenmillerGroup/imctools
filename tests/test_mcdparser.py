from .context import TestMcdParsing
from .generate_testcase import ParsingTestMCD

import unittest

from imctools.io.mcdparser import McdParser

class TestMCDparser(TestMcdParsing):
    """ Compare the current MCD parser results with some stored ones """
    def test_parser(self):
        self.parser_test(McdParser)


