from ij import IJ
from loci.plugins import BF
from ij.io import OpenDialog
from loci.formats import ImageReader
from loci.formats import MetadataTools
import i5d.Image5D
from __future__ import with_statement, division

import os
import sys
imctool_dir = os.path.join(IJ.getDirectory('plugins'),'imctools')
sys.path.append(os.path.realpath(imctool_dir))

from io import mcdparserbase

if __name__ == '__main__':
    fn = '/mnt/imls-bod/data_vito/grade1.mcd'
    with mcdparserbase.McdParserBase(fn) as testmcd:
        print(testmcd.filename)
        print(testmcd.n_acquisitions)
        # print(testmcd.get_acquisition_xml('0'))
        print(testmcd.get_acquisition_channels_xml('0'))
        print(testmcd.get_acquisition_channels('0'))
        print(len(testmcd.get_acquisition_rawdata('0')))


