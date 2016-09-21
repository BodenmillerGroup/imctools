from __future__ import with_statement, division

from ij import IJ
from loci.plugins import BF
from ij.io import OpenDialog
from ij import ImageStack
from loci.formats import ImageReader
from loci.formats import MetadataTools
import i5d.Image5D


import os
import sys
imctool_dir = os.path.join(IJ.getDirectory('plugins'),'imctools')
sys.path.append(os.path.realpath(imctool_dir))

from io import mcdparserbase

if __name__ == '__main__':
    fn = '/home/vitoz/temp/grade1.mcd'
    with mcdparserbase.McdParserBase(fn) as testmcd:
        #print(testmcd.filename)
        #print(testmcd.n_acquisitions)
        # print(testmcd.get_acquisition_xml('0'))
        #print(testmcd.get_acquisition_channels_xml('0'))
        #print(testmcd.get_acquisition_channels('0'))
        img_data = testmcd.get_acquisition_rawdata('0')
        channel_dict = testmcd.get_acquisition_channels('0')

        (n_rows, n_channels) = testmcd.get_acquisition_dimensions('0')
        buffer_size = len(img_data)
        print(buffer_size)
        print(n_channels)
        img_channels = n_channels-3


        x_vec = [int(img_data[i]) for i in range(0, buffer_size, n_channels)]
        y_vec = [int(img_data[i]) for i in range(1, buffer_size, n_channels)]
        max_x = int(max(x_vec)+1)
        max_y = int(max(y_vec)+1)
        print(max_x, max_y )
        #imp = IJ.createHyperStack('test', max_x, max_y, n_channels, 1, 1, 32)
        stack = ImageStack.create(max_x, max_y, img_channels, 32)


        #stack.setVoxel(0, 0, 0, img_data)
        for cur_chan in range(img_channels):
            cur_proc = stack.getProcessor(cur_chan+1)
            cur_values = [img_data[i] for i in range(cur_chan+3, buffer_size, n_channels)]
            for x, y, v in zip(x_vec, y_vec, cur_values):
                    cur_proc.putPixelValue(x, y, v)
            #stack.setPixels([img_data[i] for i in range(cur_chan, buffer_size, n_channels) if i < buffer_size ], cur_chan+1)

        #imp.setStack(stack, n_channels, 1, 1)
        #print(imp.getStackSize())

        #img_processor = stack.getProcessor(1)
        #img_processor.putRow(0,0,[img_data[i] for i in range(0, buffer_size, n_channels)],buffer_size)
        # idx = range(6, buffer_size, n_channels)
        # for i in range(max_y*max_x):
        #     pix[i] = img_data[idx[i]]
        i5d_img = i5d.Image5D('test', stack, n_channels, 1, 1)
        for i in range(img_channels):
            cid = '_'.join(channel_dict[i+3])
            i5d_img.getChannelCalibration(i + 1).setLabel(str(cid))

        i5d_img.setDefaultColors()
        i5d_img.show()

