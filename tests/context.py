# -*- coding: utf-8 -*-
import os
import sys
import unittest
import zipfile
from urllib.request import urlretrieve

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from .generate_testcase import ParsingTestMCD

TEST_DATA_URL = 'https://dl.dropboxusercontent.com/s/c72yegz77toutjb/testdata.zip'
TEST_DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'testdata')
TEST_ACQUISITIONS = os.path.join(TEST_DATA_FOLDER, 'acquisitions')
TEST_RESULTS = os.path.join(TEST_DATA_FOLDER, 'test_results')
EXT_MCD = '.mcd'
EXT_RESULTS = EXT_MCD + '.pickle'


class TestMcdParsing(unittest.TestCase):
    """ Compare the current MCD parser results with some stored ones """

    def get_testcases(self):
        zip_file = os.path.join(TEST_DATA_FOLDER, 'testdata.zip')
        if not os.path.isfile(zip_file):
            urlretrieve(TEST_DATA_URL, zip_file)

        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(TEST_DATA_FOLDER)

        fns_pickles = [f for f in os.listdir() if
                       f.endswith(EXT_RESULTS)]
        paths_mcd = []
        for root, dirs, files in os.walk(TEST_ACQUISITIONS):
            for f in files:
                if f.endswith(EXT_MCD):
                    paths_mcd.append(os.path.join(root, f))
        testcases = {p_mcd: os.path.join(TEST_RESULTS, f_pick)
                     for p_mcd in paths_mcd
                     for f_pick in fns_pickles if os.path.basename(p_mcd) in f_pick}
        return testcases

    def parser_test(self, Parser):
        testcases = self.get_testcases()
        for fn_mcd, testresults in testcases.items():
            testpickle = ParsingTestMCD(testresults)
            testpickle.read_testdict_pickle(testresults)

            testmcd = ParsingTestMCD(fn_mcd)
            testmcd.read_mcd(fn_mcd, Parser=Parser)
            dict_p = testpickle.testdict
            dict_m = testmcd.testdict
            self.assertSetEqual(set(dict_p['acquisition_ids']), set(dict_m['acquisition_ids']))
            for ac in dict_p['acquisition_ids']:
                ac_p = dict_p['acquisitions'][ac]
                ac_m = dict_m['acquisitions'][ac]
                for a in ['ac_desc', 'ac_rawdim', 'ac_nchan']:
                    self.assertEqual(ac_p[a], ac_m[a])
                a = 'ac_channels'
                self.assertDictEqual(ac_p[a], ac_m[a])
