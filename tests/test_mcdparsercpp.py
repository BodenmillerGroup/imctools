from .context import TestMcdParsing
from .generate_testcase import ParsingTestMCD

import unittest
import platform

if (platform.system()  != 'Java'):
    try:
        from imctools.io.mcdparsercpp import McdParserCpp
        class TestMCDparser(TestMcdParsing):
                """ Compare the current MCD parser results with some stored ones """
                def test_parser(self):
                    self.parser_test(McdParserCpp)
    except:
        pass
