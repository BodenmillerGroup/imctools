import os

import imctools.io.mcdparserbase as mcdparserbase
import pickle
import time

class ParsingTestMCD(object):
    """
    A helper class to generate testcased.
    This can be used to load an mcd metadata with a parser and
    save the results as a pickle.

    Thus the testcase can be reloaded for testing and compared to an
    the results from changed implementation. This should help to find
    unwanted changes in the outhe results from changed implementation. 
    This should help to find unwanted changes in the output/api.
    """
    def __init__(self, example_fn):
        self.filename = example_fn
        self.testdict = dict()

    def read_mcd(self, path, Parser=None):
        if Parser is None:
            Parser = mcdparserbase.McdParserBase
        self.mcd = Parser(path)
        self.populate_testdict()
        self.mcd.close()

    
    def read_testdict_pickle(self, path):
        self.load_testdict_pickle(path)


    def populate_testdict(self):
        mcd = self.mcd
        self.testdict['acquisition_ids'] = mcd.acquisition_ids
        acdict = dict()
        self.testdict['acquisitions'] = acdict
        for ac in mcd.acquisition_ids:
            acdict[ac] = self.populate_ac_testdict(ac)

    def populate_ac_testdict(self, ac):
        tdict = dict()
        mcd = self.mcd

        tdict['ac_desc'] = mcd.get_acquisition_description(ac)
        tdict['ac_rawdim'] = (len(mcd.get_acquisition_rawdata(ac)),
                                  len(mcd.get_acquisition_rawdata(ac)[0]))
        tdict['ac_channels'] = mcd.get_acquisition_channels(ac)
        tdict['ac_nchan' ] = mcd.get_nchannels_acquisition(ac)
        return tdict

    def load_testdict_pickle(self, path):
        with open(path, 'rb') as f:
            self.testdict = pickle.load(f)
        

    def dump_testdict_pickle(self, path):
        sep = '_'
        fn = sep.join([time.strftime("%Y%m%d"), self.filename])+'.pickle'

        with open( os.path.join(path, fn), 'wb') as outfile:
            pickle.dump(self.testdict, outfile, protocol=2)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Generates a testcase from an imc file',
        prog='generate_testcase')
    parser.add_argument('imc_filename', type=str,
                        help='Path to the imcfile to generate the testcase from')
    parser.add_argument('out_folder', type=str, default=None)

    args = parser.parse_args()

    if args.out_folder is None:
        args.out_folder = os.path.split(args.imc_filename)[0]

    filename = os.path.split(args.imc_filename)[1]
    
    test = ParsingTestMCD(filename)
    test.read_mcd(args.imc_filename)
    test.dump_testdict_pickle(args.out_folder)


