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

    def get_imc_aquisition(self):
        """
        Returns the imc acquisition object
        :return:
        """

        return ImcAcquisitionBase('0', self.filename,
                                  self.data,
                                  self.channel_names,
                                  None,
                                  original_metadata=None ,
                                  image_description=None,
                                  origin=self.origin)



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
        print(data[0])
        self.data = data
        self.channel_names = channel_names

    def parse_csv2(self, filename, first_col=3):
        with open(filename, 'r') as txtfile:
            header = txtfile.readline().split('\t')
            channel_names = header[first_col:]
            data = [[float(v) for v in row.split('\t')[first_col:]] for row in txtfile]
        self.data = data
        self.channel_names = channel_names


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
            print(len(rowar)/nchan)
            data = [rowar[(i*nchan):(i*nchan+nchan)] for i in range(nrow)]
        self.data = data
        self.channel_names = channel_names


if __name__ == '__main__':
    fn = '/home/vitoz/mnt/imls-bod/Stefanie/2016/20160920/HIER_healthy/HIER_healthy_1_0_HIER1_1.txt'
    #fn = '/home/vitoz/temp/20150330_IS2335_5um_3_site1_ac2_200hz_2200x2200.txt'
    imc_txt = TxtParserBase(fn)
    imc_ac = imc_txt.get_imc_aquisition()