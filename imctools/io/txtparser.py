from __future__ import with_statement, division

import csv
from imcacquisition import ImcAcquisition
from txtparserbase import TxtParserBase
from imctools.io.abstractparser import AbstractParser
import array
import numpy as np

class TxtParser(TxtParserBase):
    """
    Loads and strores an IMC .txt file
    """

    def __init__(self, filename):
        super(TxtParser, self).__init__(filename)
        self.data = np.array(self.data)

    def get_imc_aquisition(self):
        """
        Returns the imc acquisition object
        :return:
        """

        return ImcAcquisition('0', self.filename,
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
        # find which version it is
        names = [n.strip("\r") for n in names]
        names = [n.strip("\n") for n in names]
        names = [n.strip() for n in names]
        # string of sort asbsdf(mn123di)
        if names[0].rfind(')') == (len(names[0])-1):
            #get m123di

            names = [n[(n.rfind('(')+1):(n.rfind(')'))] for n in names]

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



if __name__ == '__main__':
    import matplotlib.pyplot as plt
    fn = '/mnt/imls-bod/Stefanie/2016/20160920/HIER_healthy/HIER_healthy_1_0_HIER1_1.txt'
    #fn = '/mnt/imls-bod/data_vito/Spheres/20160330_BigInspheroIMC2/20150330_IS2335_5um_3_site1_ac2_200hz_2200x2200/20150330_IS2335_5um_3_site1_ac2_200hz_2200x2200.txt'
    #fn = '/home/vitoz/temp/20150330_IS2335_5um_3_site1_ac2_200hz_2200x2200.txt'
    imc_txt = TxtParser(fn)
    imc_ac = imc_txt.get_imc_aquisition()
    iw = imc_ac.get_image_writer('/home/vitoz/temp/test_iridium.ome.tiff', mass=['191', '193'])
    iw.save_image(mode='ome')