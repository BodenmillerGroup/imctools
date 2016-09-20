import os
import numpy as np
import tifffile
from bioformats import omexml as ome

class TiffWriter(object):
    """

    """
    pixeltype_dict = ({np.int64().dtype: ome.PT_INT16,
                       np.float32().dtype: ome.PT_FLOAT})

    def __init__(self, file_name, img_stack, pixeltype =None, channel_name=None, original_description=None):
        self.file_name = file_name
        self.img_stack = img_stack
        self.channel_name = channel_name

        if pixeltype is None:
            pixeltype = self.pixeltype_dict[img_stack.dtype]
        self.pixeltype = pixeltype

        if original_description is None:
            original_description = ''

        self.original_description = original_description



    def save_image(self):
        #TODO: add original metadata somehow
        xml = self.get_xml()
        fn_out = self.file_name

        tifffile.imsave(fn_out, self.img_stack.swapaxes(2,0), compress=9, imagej=False,
                        description=xml)

    @property
    def nchannels(self):
        return self.img_stack.shape[2]


    def get_xml(self):
        img = self.img_stack
        omexml = ome.OMEXML()
        omexml.image(0).Name = os.path.basename(self.file_name)
        p = omexml.image(0).Pixels
        p.SizeX = img.shape[0]
        p.SizeY = img.shape[1]
        p.SizeC = self.nchannels
        p.SizeT = 1
        p.SizeZ = 1
        p.DimensionOrder = ome.DO_XYCZT
        p.PixelType = self.pixeltype
        p.channel_count = self.nchannels
        for i in range(self.nchannels):
            channel_info = self.channel_name[i]
            p.Channel(i).set_SamplesPerPixel(1)
            p.Channel(i).set_Name(channel_info)
            p.Channel(i).set_ID('channel' + str(i))

        # omexml.structured_annotations.add_original_metadata(
        #     ome.OM_SAMPLES_PER_PIXEL, str(1))

        xml = omexml.to_xml()
        return xml