from __future__ import with_statement, division

import csv
from imctools.io.imcacquisitionbase import ImcAcquisitionBase
from imctools.io.abstractparserbase import AbstractParserBase
import array
TXT_FILENDING='.txt'

class TxtParserBase(AbstractParserBase):
    """
    Loads and strores an IMC .txt file
    """

    def __init__(self, filename, filehandle=None):
        AbstractParserBase.__init__(self)
        self.filename = filename
        if filehandle is None:
            with open(filename, 'r') as txtfile:
                self.parse_csv3(txtfile)
        else:
            filehandle.seek(0)
            self.parse_csv3(filehandle)
        self.origin ='txt'
        self.channel_labels = self.channel_metals[:]
        self.channel_metals[3:] = self.clean_channel_metals(self.channel_metals[3:])

    @property
    def ac_id(self):
        ac_id = self._txtfn_to_ac(self.filename)
        return ac_id

    @staticmethod
    def _txtfn_to_ac(fn):
        return fn.rstrip(TXT_FILENDING).split('_')[-1]

    def get_imc_acquisition(self):
        """
        Returns the imc acquisition object
        :return:
        """
        dat = self.data
        img = self._reshape_long_2_cyx(dat, is_sorted=True)
        ac_id = self.ac_id

        return ImcAcquisitionBase(ac_id, self.filename,
                                  img,
                                  self.channel_metals,
                                  self.channel_labels,
                                  original_metadata=None,
                                  image_description=None,
                                  origin=self.origin,
                                  offset=3)

    @staticmethod
    def clean_channel_metals(names):
        """
        clean the names to be nice
        :return:
        """
        print(names)
        # find which version it is
        names = [n.strip("\r") for n in names]
        names = [n.strip("\n") for n in names]
        names = [n.strip() for n in names]
        # string of sort asbsdf(mn123di)
        if names[0].rfind(')') == (len(names[0])-1):
            #get m123di

            names = [n[(n.rfind('(')+1):(n.rfind(')'))] for n in names]
            print(names)

        # string of sort aasbas_mn123
        elif '_' in names[0]:
            names = [n.split('_')[-1] for n in names]

        # else do nothing
        else:
            return names

        # else there is the bug where (123123di)
        names = [n.rstrip('di') for n in names]
        names = [n.rstrip('Di') for n in names]
        if names[0][0].isdigit():
            names = [n[(int(len(n)/2)):] for n in names]

        return names

    def parse_csv(self, txtfile, first_col=3):
        txtreader = csv.reader(txtfile, delimiter='\t')
        header = txtreader.next()
        channel_names = header[first_col:]
        nchan = len(channel_names)
        txtreader = csv.reader(txtfile, delimiter='\t',
                               quoting=csv.QUOTE_NONNUMERIC)
        txtreader.next()
        data = list()
        for row in txtreader:
            rowar = array.array('f')
            rowar.fromlist(row[first_col:])
            data.append(rowar)
        self.data = data
        self.channel_metals = channel_names

    def parse_csv2(self, txtfile, first_col=3):
        header = txtfile.readline().split('\t')
        channel_names = header[first_col:]
        data = [[float(v) for v in row.split('\t')[first_col:]] for row in txtfile]
        self.data = data
        self.channel_metals = channel_names


    def parse_csv3(self, txtfile, first_col=3):
        """
        The fastest  csv parser so far
        :param filename:
        :param first_col: First column to consider
        :return:
        """
        header = txtfile.readline().split('\t')
        channel_names = header[first_col:]
        nchan = len(channel_names)
        rowar = array.array('f')
        for row in txtfile:
            for v in row.split('\t')[first_col:]:
                rowar.append(float(v))
        nrow = int(len(rowar)/nchan)
        data = [rowar[(i*nchan):(i*nchan+nchan)] for i in range(nrow)]
        self.data = data
        self.channel_metals = channel_names


if __name__ == '__main__':
    import timeit
    #fn = '/home/vitoz/temp/grade1_1_0_A0_0.txt'
    fn = '/media/vitoz/datahdd/data/site1_0_A0_0 - Copy.txt'
    #fn = '/home/vitoz/temp/20150330_IS2335_5um_3_site1_ac2_200hz_2200x2200.txt'
    tic = timeit.default_timer()
    imc_txt = TxtParserBase(fn)
    print(timeit.default_timer()-tic)
    tic = timeit.default_timer()
    imc_txt = imc_txt.parse_csv3(fn)
    print(timeit.default_timer()-tic)
    imc_ac = imc_txt.get_imc_acquisition()
    rowimg = imc_ac._data[1]
    print(rowimg[0][:3])
    print(rowimg[1][:3])
    print(rowimg[2][:3])
    import numpy as np
    import matplotlib.pyplot as plt
    print(np.asarray(rowimg))


    #print(imc_ac.get_img_by_channel_nr(1))
