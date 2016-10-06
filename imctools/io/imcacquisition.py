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
                 original_metadata=None, image_description=None, origin=None):
        """

        :param filename:
        """
        super(ImcAcquisition, self).__init__(image_ID, original_file, data, channel_metal, channel_labels,
                                             original_metadata, image_description, origin)

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
            order = range(self.n_channels)


        out_names = [label +'_' + name for label, name in zip(self.channel_labels, self.channel_metals)]
        out_names = [out_names[i] for i in order]
        dat = np.array(self.get_img_stack_cyx(order), dtype=np.float32).swapaxes(2,0)
        tw = TiffWriter(filename, dat, channel_name=out_names, original_description=self.original_metadata)
        return tw

    def save_analysis_tiff(self, filename, metals=None):
        pass

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from imctools.io.mcdparser import McdParser
    from imctools.io.ometiffparser import OmetiffParser
    fn = '/home/vitoz/temp/20150330_IS2335_5um_3_site1_ac2_200hz_2200x2200/20150330_IS2335_5um_3_site1_ac2_200hz_2200x2200.ome.tiff'
    #with OmetiffParser(fn) as testmcd:
    testmcd = OmetiffParser(fn)
    #print(testmcd.filename)
    #print(testmcd.n_acquisitions)
    #print(testmcd.get_acquisition_xml('0'))
    #print(testmcd.get_acquisition_channels_xml('0'))
    #print(testmcd.get_acquisition_channels('0'))
    imc_img = testmcd.get_imc_acquisition()
    print(imc_img)
    img = imc_img.get_img_by_metal('X')
    # plt.figure()OmetiffParser(fn)
    # plt.imshow(np.array(img).squeeze())
    # plt.show()


    print(imc_img.channel_metals)
    imc_img.save_image('/home/vitoz/temp/20150330_IS2335_5um_3_site1_ac2_200hz_2200x2200/test_iridium.tiff', mass=['172', '173', '174', '175', '176', '191', '193'])
