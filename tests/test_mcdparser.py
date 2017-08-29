from .context import TESTCASES
from .generate_testcase import ParsingTestMCD
import unittest

class TestMCDparsing(unittest.TestCase):
    """ Compare the current MCD parser results with some stored ones """

    def test_results(self):
        for fn_mcd, testresults in TESTCASES.items():
            testpickle= ParsingTestMCD(testresults)
            testpickle.read_testdict_pickle(testresults)

            testmcd = ParsingTestMCD(fn_mcd)
            testmcd.read_mcd(fn_mcd)

            self.assertDictEqual(testmcd.testdict, testpickle.testdict)
