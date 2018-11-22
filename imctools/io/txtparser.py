from __future__ import with_statement, division

import csv
from imctools.io.imcacquisition import ImcAcquisition
from imctools.io.abstractparser import AbstractParser
import array

try:
    import numpy as np
    _have_numpy = True
except ImportError as ix:
    _have_numpy = False

TXT_FILENDING='.txt'


class TxtParser(AbstractParser):
    """
    Loads and strores an IMC .txt file
    """

    def __init__(self, filename, filehandle=None):
        AbstractParser.__init__(self)
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
        if _have_numpy:
            self.data = np.array(self.data)

    @property
    def ac_id(self):
        ac_id = self.txtfn_to_ac(self.filename)
        return ac_id

    @staticmethod
    def txtfn_to_ac(fn):
        return fn.rstrip(TXT_FILENDING).split('_')[-1]

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

    def get_imc_acquisition(self):
        """
        Returns the imc acquisition object
        :return:
        """
        dat = self.data
        img = self._reshape_long_2_cyx(dat, is_sorted=True)
        ac_id = self.ac_id

        return ImcAcquisition(ac_id, self.filename,
                              img,
                              self.channel_metals,
                              self.channel_labels,
                              original_metadata=None,
                              image_description=None,
                              origin=self.origin,
                              offset=3)

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
        The fastest csv parser so far
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
