from __future__ import with_statement, division

import csv
from imcacquisitionbase import ImcAcquisitionBase
from imctools.io.abstractparser import AbstractParser
import array


class TxtParserBase(AbstractParser):
    """
    Loads and strores an IMC .txt file
    """

    def __init__(self, filename):
        super(TxtParserBase, self).__init__()
        self.parse_csv3(filename)
        self.filename = filename
        self.origin ='txt'
        self.channel_labels = self.channel_metals[:]
        self.channel_metals[3:] = self.clean_channel_metals(self.channel_metals[3:])

    def get_imc_aquisition(self):
        """
        Returns the imc acquisition object
        :return:
        """

        return ImcAcquisitionBase('0', self.filename,
                                  self.data,
                                  self.channel_metals,
                                  self.channel_labels,
                                  original_metadata=None,
                                  image_description=None,
                                  origin=self.origin)

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
        print(1)
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

    def parse_csv(self, filename, first_col=3):
        with open(filename, 'r') as txtfile:
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

    def parse_csv2(self, filename, first_col=3):
        with open(filename, 'r') as txtfile:
            header = txtfile.readline().split('\t')
            channel_names = header[first_col:]
            data = [[float(v) for v in row.split('\t')[first_col:]] for row in txtfile]
        self.data = data
        self.channel_metals = channel_names


    def parse_csv3(self, filename, first_col=3):
        """
        The fastest  csv parser so far
        :param filename:
        :param first_col: First column to consider
        :return:
        """
        with open(filename, 'r') as txtfile:
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
    fn = '/mnt/imls-bod/Stefanie/2016/20160920/HIER_healthy/HIER_healthy_1_0_HIER1_1.txt'
    #fn = '/mnt/imls-bod/data_vito/Spheres/20160330_BigInspheroIMC2/20150330_IS2335_5um_3_site1_ac2_200hz_2200x2200/20150330_IS2335_5um_3_site1_ac2_200hz_2200x2200.txt'
    #fn = '/home/vitoz/temp/20150330_IS2335_5um_3_site1_ac2_200hz_2200x2200.txt'
    imc_txt = TxtParserBase(fn)
    imc_ac = imc_txt.get_imc_aquisition()