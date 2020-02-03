import os
import sys
import zipfile
from urllib.request import urlretrieve

from tests.helpers import ParseTestMCD

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

TEST_DATA_URL = 'https://dl.dropboxusercontent.com/s/so1zgn9p9kdml4x/testdata_v2.zip'
TEST_DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'testdata')
TEST_ACQUISITIONS = os.path.join(TEST_DATA_FOLDER, 'acquisitions')
TEST_RESULTS = os.path.join(TEST_DATA_FOLDER, 'test_results')
EXT_MCD = '.mcd'
EXT_RESULTS = EXT_MCD + '.pickle'


class TestMcdParser:
    """ Compare the current MCD parser results with some stored ones """

    def test_parser(self):
        test_cases = TestMcdParser._get_test_cases()
        for fn_mcd, testresults in test_cases.items():
            testpickle = ParseTestMCD(testresults)
            testpickle.load_test_dict_pickle(testresults)

            testmcd = ParseTestMCD(fn_mcd)
            testmcd.read_mcd(fn_mcd)
            dict_p = testpickle.testdict
            dict_m = testmcd.testdict
            assert set(dict_p['acquisition_ids']) == set(dict_m['acquisition_ids'])
            for ac in dict_p['acquisition_ids']:
                ac_p = dict_p['acquisitions'][ac]
                ac_m = dict_m['acquisitions'][ac]
                for a in ['ac_desc', 'ac_rawdim', 'ac_nchan']:
                    assert ac_p[a] == ac_m[a]
                a = 'ac_channels'
                assert str(ac_p[a]) == str(ac_m[a])

    @staticmethod
    def _get_test_cases():
        zip_file = os.path.join(TEST_DATA_FOLDER, 'testdata_v2.zip')
        if not os.path.isfile(zip_file):
            urlretrieve(TEST_DATA_URL, zip_file)

        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(TEST_DATA_FOLDER)

        fns_pickles = [f for f in os.listdir(TEST_RESULTS) if
                       f.endswith(EXT_RESULTS)]
        paths_mcd = []
        for root, dirs, files in os.walk(TEST_ACQUISITIONS):
            for f in files:
                if f.endswith(EXT_MCD):
                    paths_mcd.append(os.path.join(root, f))
        test_cases = {p_mcd: os.path.join(TEST_RESULTS, f_pick)
                     for p_mcd in paths_mcd
                     for f_pick in fns_pickles if os.path.basename(p_mcd) in f_pick}
        return test_cases


if __name__ == '__main__':
    parser = TestMcdParser()
    parser.test_parser()
