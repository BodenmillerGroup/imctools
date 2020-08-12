import os

import pickle
import time

from imctools.io.mcd.mcdparser import McdParser


class ParseTestMCD:
    """
    A helper class to generate a test case.
    This can be used to load an mcd metadata with a parser and
    save the results as a pickle.

    Thus the test case can be reloaded for testing and compared to an the results from changed implementation.
    This should help to find unwanted changes in the output/api.
    """

    def __init__(self, example_fn):
        self.filename = example_fn
        self.testdict = dict()

    def read_mcd(self, filepath: str):
        self.parser = McdParser(filepath)
        self.populate_test_dict()
        self.parser.close()

    def populate_test_dict(self):
        ac_ids = [a.id for a in self.parser.session.acquisitions.values()]
        self.testdict['acquisition_ids'] = ac_ids
        ac_dict = dict()
        self.testdict['acquisitions'] = ac_dict
        for ac_id in ac_ids:
            ac_dict[ac_id] = self.populate_ac_test_dict(ac_id)

    def populate_ac_test_dict(self, acquisition_id: int):
        test_dict = dict()
        ac = self.parser.session.acquisitions.get(acquisition_id)
        test_dict['ac_desc'] = ac.description
        test_dict['ac_rawdim'] = (len(self.parser._get_acquisition_raw_data(ac)), len(self.parser._get_acquisition_raw_data(ac)[0]))
        test_dict['ac_channels'] = ac.channels
        test_dict['ac_nchan'] = ac.n_channels
        return test_dict

    def load_test_dict_pickle(self, path):
        with open(path, 'rb') as f:
            self.testdict = pickle.load(f)

    def dump_test_dict_pickle(self, path):
        sep = '_'
        fn = sep.join([time.strftime("%Y%m%d"), self.filename]) + '.pickle'

        with open(os.path.join(path, fn), 'wb') as outfile:
            pickle.dump(self.testdict, outfile, protocol=2)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generates a test case from an IMC file', prog='generate_testcase')
    parser.add_argument('mcd_filename', help='Path to the MCD file to generate the test case from')
    parser.add_argument('out_folder', default=None)
    args = parser.parse_args()

    if args.out_folder is None:
        args.out_folder = os.path.split(args.mcd_filename)[0]

    filename = os.path.split(args.mcd_filename)[1]

    test = ParseTestMCD(filename)
    test.read_mcd(args.mcd_filename)
    test.dump_test_dict_pickle(args.out_folder)
