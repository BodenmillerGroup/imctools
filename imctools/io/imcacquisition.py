"""
This defines the IMC acquisition base class
"""
import os
import numpy as np
from imctools.io.tiffwriter import TiffWriter
import xml.etree.ElementTree as et
from imctools.io.imcacquisitionbase import ImcAcquisitionBase


class ImcAcquisition(ImcAcquisitionBase):
    """
     An Image Acquisition Object representing a single acquisition

    """

    def __init__(self, image_ID, original_file, data, channel_names, channel_labels,
                 original_metadata=None, image_description=None, origin=None):
        """

        :param filename:
        """
        super(ImcAcquisition, self).__init__(image_ID, original_file, data, channel_names, channel_labels,
                 original_metadata, image_description, origin)

    def save_image(self, filename):
        tw = self.get_image_writer(filename)
        tw.save_image()

    def get_image_writer(self, filename):
        out_names = [label+'_'+name for label, name in zip(self.channel_labels, self.channel_names)]
        dat = np.array(self.get_img_stack_cyx(), dtype=np.float32).swapaxes(2,0)
        tw = TiffWriter(filename, dat, channel_name=out_names, original_description=self.original_metadata)
        return tw

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from imctools.io.mcdparser import McdParser
    fn = '/mnt/imls-bod/data_vito/grade1.mcd'
    with McdParser(fn) as testmcd:
        print(testmcd.filename)
        print(testmcd.n_acquisitions)
        #print(testmcd.get_acquisition_xml('0'))
        print(testmcd.get_acquisition_channels_xml('0'))
        print(testmcd.get_acquisition_channels('0'))
        imc_img = testmcd.get_imc_acquisition('0')
        img = imc_img.get_img_by_name('X')
        plt.figure()
        plt.imshow(np.array(img).squeeze())
        plt.show()
        imc_img.save_image('/mnt/imls-bod/data_vito/test1.tiff')
