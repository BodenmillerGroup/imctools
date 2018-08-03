import os
import numpy as np
import tifffile
import imctools.external.omexml as ome

from xml.etree import cElementTree as ElementTree

import sys
if sys.version_info.major == 3:
    from io import StringIO
    uenc = 'unicode'
else:
    from cStringIO import StringIO
    uenc = 'utf-8'


class TiffWriter(object):
    """

    """
    pixeltype_dict = ({np.int64().dtype: ome.PT_FLOAT,
                       np.int32().dtype: ome.PT_INT32,
                       np.int16().dtype: ome.PT_INT16,
                       np.uint16().dtype: ome.PT_UINT16,
                       np.uint32().dtype: ome.PT_UINT32,
                       np.uint8().dtype: ome.PT_UINT8,
                       np.float32().dtype: ome.PT_FLOAT,
                       np.float64().dtype: ome.PT_FLOAT
                       })

    def __init__(self, file_name, img_stack, pixeltype =None, channel_name=None, original_description=None, fluor=None):
        self.file_name = file_name
        self.img_stack = img_stack
        self.channel_name = channel_name
        if fluor is None:
            self.fluor = channel_name
        else:
            self.fluor = fluor

        if pixeltype is None:
            pixeltype = self.pixeltype_dict[img_stack.dtype]
        self.pixeltype = pixeltype

        if original_description is None:
            original_description = ''

        self.original_description = original_description

    def save_image(self, mode='imagej', compression=0, dtype=None, bigtiff=True):
        #TODO: add original metadata somehow
        fn_out = self.file_name
        img = self.img_stack.swapaxes(2, 0)
        if dtype is not None:
            dt = np.dtype(dtype)
        else:
            dt = np.dtype(self.pixeltype)
            img = img.astype(dt)
        # img = img.reshape([1,1]+list(img.shape)).swapaxes(2, 0)
        if mode == 'imagej':
            tifffile.imsave(fn_out, img, compress=compression, imagej=True,
                            bigtiff=bigtiff)
        elif mode == 'ome':
            xml = self.get_xml(dtype=dtype)
            tifffile.imsave(fn_out, img, compress=compression, imagej=False,
                            description=xml, bigtiff=bigtiff)

    # def save_xml(self):
    #     xml = self.get_xml()
    #     with open(self.file_name+'.xml', 'w') as f:
    #         f.write(xml)
    #
    # def save_ome_tiff(self):
    #     #TODO: does not work
    #     img = self.img_stack.astype(np.uint16)
    #     print(img.shape)
    #     javabridge.start_vm(class_path=bioformats.JARS)
    #     bioformats.write_image(self.file_name, pixels=img, pixel_type='uint16', c=0, z=0, t=0,
    #                            size_z=1, size_t=1, channel_metals=self.channel_name)
    #     javabridge.kill_vm()

    @property
    def nchannels(self):
        return self.img_stack.shape[2]

    def get_xml(self, dtype=None):
        if dtype is None:
            pixeltype = self.pixeltype_dict[dtype]
        else:
            pixeltype = self.pixeltype
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
        p.PixelType = pixeltype
        p.channel_count = self.nchannels
        for i in range(self.nchannels):
            channel_info = self.channel_name[i]
            p.Channel(i).set_SamplesPerPixel(1)
            p.Channel(i).set_Name(channel_info)
            p.Channel(i).set_ID('Channel:0:' + str(i))
            p.Channel(i).node.set('Fluor', self.fluor[i])
        # adds original metadata as annotation
        if self.original_description is not None:
            if isinstance(self.original_description,
                          type(ElementTree.Element(1))):
                result = StringIO()
                ElementTree.ElementTree(self.original_description).write(result,
                                                          encoding=uenc, method="xml")
                desc = result.getvalue()
            else:
                desc = str(self.original_description)

            omexml.structured_annotations.add_original_metadata(
                'MCD-XML',
                desc)

        xml = omexml.to_xml()
        return xml
