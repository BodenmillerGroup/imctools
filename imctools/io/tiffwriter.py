import os
import numpy as np
import tifffile
import imctools.external.omexml as ome
from xml.etree import cElementTree as ElementTree
import sys

import warnings

from imctools.io import change_dtype, CHANGE_DTYPE_LB_WARNING, CHANGE_DTYPE_UB_WARNING

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
                       np.float64().dtype: ome.PT_DOUBLE
                       })
    pixeltype_np = {
            ome.PT_FLOAT: np.dtype('float32'),
            ome.PT_DOUBLE: np.dtype('float64'),
            ome.PT_UINT8: np.dtype('uint8'),
            ome.PT_UINT16: np.dtype('uint16'),
            ome.PT_UINT32: np.dtype('uint32'),
            ome.PT_INT8: np.dtype('int8'),
            ome.PT_INT16: np.dtype('int16'),
            ome.PT_INT32: np.dtype('int32')
        }
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

    def save_image(self, mode='imagej', compression=0, dtype=None, bigtiff=None):
        """
        Saves the image as a tiff
        :param mode: Specifies the tiff writing mode. Either 'imagej' or 'ome'
                    for .ome.tiff's
        :param compression: Tiff compression level.
                            Default to 0 (no compression)
                            Internaly compressed tiffs are more incompatible and
                            not memory-mappable
        :param dtype: dtype of the  output tiff.
                      Default: take the dtype of the original data
        :param bigtiff: should the tiff be writen as a 'bigtiff'?
                        'bigtiff' support >4gb of data, but are less widely
                        compatible.
                        Default: for 'imagej' mode: False
                                 for 'ome' mode: True
        """
        #TODO: add original metadata somehow
        fn_out = self.file_name
        img = self.img_stack.swapaxes(2, 0)
        if dtype is not None:
            dt = np.dtype(dtype)
        else:
            dt = self.pixeltype_np[self.pixeltype]
        img = change_dtype(img, dt)
        # img = img.reshape([1,1]+list(img.shape)).swapaxes(2, 0)
        if mode == 'imagej':
            if bigtiff is None:
                bigtiff=False
            tifffile.imsave(fn_out, img, compress=compression, imagej=True,
                            bigtiff=bigtiff)
        elif mode == 'ome':
            if bigtiff is None:
                bigtiff=True
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
        if dtype is not None:
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
