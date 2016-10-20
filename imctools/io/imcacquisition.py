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

    def __init__(self, image_ID, original_file, data, channel_metal, channel_labels,
                 original_metadata=None, image_description=None, origin=None, offset=0):
        """

        :param filename:
        """
        ImcAcquisitionBase.__init__(self, image_ID, original_file, data, channel_metal, channel_labels,
                                             original_metadata, image_description, origin, offset=offset)

    def save_image(self, filename, metals=None, mass=None):
        tw = self.get_image_writer(filename, metals=metals, mass=mass)
        tw.save_image()

    def get_image_writer(self, filename, metals=None, mass=None):
        """
        Get an image writer with the right data
        :param filename:
        :param metals:
        :return:
        """

        if metals is not None:
            order = self.get_metal_indices(metals)

        elif mass is not None:
            order = self.get_mass_indices(mass)
        else:
            order = [i for i in range(self.n_channels)]

        out_names = [self.channel_labels[i] for i in order]
        out_fluor = [self.channel_metals[i] for i in order]
        dat = np.array(self.get_img_stack_cxy(order), dtype=np.float32).swapaxes(2,0)
        tw = TiffWriter(filename, dat, channel_name=out_names, original_description=self.original_metadata, fluor=out_fluor)
        return tw

    def save_analysis_tiff(self, filename, metals=None):
        pass

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from imctools.io.mcdparser import McdParser
    from imctools.io.ometiffparser import OmetiffParser
    fn = '/home/vitoz/temp/HIER_healthy_4_3_HIER5_4.ome.tiff'
    #with OmetiffParser(fn) as testmcd:
    testmcd = OmetiffParser(fn)
    #print(testmcd.filename)
    #print(testmcd.n_acquisitions)
    #print(testmcd.get_acquisition_xml('0'))
    #print(testmcd.get_acquisition_channels_xml('0'))
    #print(testmcd.get_acquisition_channels('0'))
    imc_img = testmcd.get_imc_acquisition()
    print(imc_img.n_channels)
    print(imc_img.get_mass_indices(['191', '193']))
    # img = imc_img.get_img_by_metal('X')
    # plt.figure()OmetiffParser(fn)
    # plt.imshow(np.array(img).squeeze())
    # plt.show()


    print(imc_img.channel_metals)
    iw = imc_img.get_image_writer('/home/vitoz/temp/test_iridium.ome.tiff', mass=['191', '193'])
    iw.save_image(mode='ome')
