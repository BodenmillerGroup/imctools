from __future__ import with_statement, division

import ij.process as process
from ij import ImageStack
import i5d.Image5D
import i5d

import struct

from loci.formats import ImageReader , MetadataTools, IFormatWriter, FormatTools
import ome.xml.model.enums.DimensionOrder as DimensionOrder
import ome.xml.model.primitives.PositiveInteger as PositiveInteger
import ome.xml.model.primitives.NonNegativeInteger  as NonNegativeInteger
import ome.xml.model.enums.PixelType as PixelType
from loci.formats import ImageWriter, ImageReader
from loci.plugins import BF
import ome.units.quantity.Length as Length
import ome.units.UNITS as units

import loci.common.DataTools as DataTools

import xml.etree.ElementTree as et


def convert_imc_to_image(imc_acquisition):
    """
    Load an MCD and convert it to a image5d Tiff
    :param filename: Filename of the MCD
    :return: an image5d image
    """
    ac_id = imc_acquisition.image_ID
    print('Contstruct image from data: %s' %ac_id)

    img_channels = imc_acquisition.n_channels
    channel_names = imc_acquisition.channel_metals
    channel_labels = imc_acquisition.channel_labels

    img_data = imc_acquisition.get_img_stack_cxy()

    print('Add planes to stack:')
    imgstack = stack_to_imagestack(img_data)

    file_name = imc_acquisition.original_filename.replace('.mcd','')
    file_name = file_name.replace('.txt', '')
    description = imc_acquisition.image_description
    if description is not None:
        file_name = '_'.join((file_name,'a'+ac_id, 'd'+description))
    else:
        file_name = '_'.join((file_name, 'a' + ac_id))



    if channel_labels is not None:
        channel_ids = [lab + '_' + name for  name, lab in
                       zip(channel_names, channel_labels)]
    else:
        channel_ids = channel_names
    i5d_img = get_image5d(file_name, imgstack,  channel_ids)

    i5d_img.setDefaultColors()
    print('finished image: %s' %ac_id)

    return i5d_img


def stack_to_imagestack(cxy_stack, img_stack=None):
    """

    :param cxy_stack:
    :param img_stack:
    :return:
    """
    c, x, y = (len(cxy_stack), len(cxy_stack[0]), len(cxy_stack[0][0]))
    if img_stack is None:
        img_stack = ImageStack(x, y)

    for i in range(c):
        cur_proc = process.FloatProcessor(cxy_stack[i])
        img_stack.addSlice(cur_proc)

    return img_stack


def get_image5d(imgName, img_stack, channel_names):
    """

    :param imgName:
    :param img_stack:
    :param channel_names:
    :return:
    """

    nchannels = len(channel_names)
    i5dimg = i5d.Image5D(imgName, img_stack, nchannels,1,1)

    for i,cid in enumerate(channel_names):
        i5dimg.getChannelCalibration(i+1).setLabel(str(cid))

    i5dimg.setDefaultColors()
    return i5dimg

def load_ome_img(file_name):
    """

    :param file_name:
    :return:
    """
    imps = BF.openImagePlus(file_name)
    imag = imps[0]
    # parse metadata
    reader = ImageReader()
    omeMeta = MetadataTools.createOMEXMLMetadata()
    reader.setMetadataStore(omeMeta)
    reader.setId(file_name)
    print(omeMeta)
    reader.close()

    return (imag, omeMeta)

def generate_ome_fromimc(imc_acquisition):
    """

    :param imc_acquisition:
    :return:
    """

    x, y, c = imc_acquisition.shape
    print(x,y,c)
    metadata = MetadataTools.createOMEXMLMetadata()
    filename= '/home/vitoz/temp/test.ome.tiff'
    MetadataTools.populateMetadata(metadata, 0, filename, True, "XYZTC",
                                   FormatTools.getPixelTypeString(6), x, y, 1, c, 1, 1)
    if imc_acquisition.origin == 'mcd':
        ac_id = imc_acquisition.image_ID
        meta_xml = et.XML(imc_acquisition.original_metadata)
        ns = '{'+meta_xml.tag.split('}')[0].strip('{')+'}'

        channel_xml = [channel_xml for channel_xml in meta_xml.findall(ns + 'AcquisitionChannel')
         if channel_xml.find(ns + 'AcquisitionID').text == ac_id]

        ac_xml = [tx for tx in meta_xml.findall(ns + 'Acquisition')
         if tx.find(ns + 'ID').text == ac_id][0]
        # AcquisitionDate = ac_xml.find(ns+'StartTimeStamp').text
        # Description = ac_xml.find(ns+'Description').text
        # AblationPower = ac_xml.find(ns + 'AblationPower').text
        # AblationDistanceBetweenShots = ac_xml.find(ns + 'AblationDistanceBetweenShots').text
        # AblationFrequency = ac_xml.find(ns + 'AblationFrequency').text
        # ROIID = ac_xml.find(ns + 'ROIID').text
        # OrderNumber = ac_xml.find(ns + 'OrderNumber').text
        # SignalType = ac_xml.find(ns + 'SignalType').text
        # DataStartOffset = ac_xml.find(ns + 'DataStartOffset').text
        # DataEndOffset = ac_xml.find(ns + 'DataEndOffset').text
        # StartTimeStamp = ac_xml.find(ns + 'StartTimeStamp').text
        # EndTimeStamp = ac_xml.find(ns + 'EndTimeStamp').text
        # SegmentDataFormat = ac_xml.find(ns + 'SegmentDataFormat').text
        # ValueBytes = ac_xml.find(ns + 'ValueBytes').text
        #
        # chan_order = [int(cxml.find(ns+'OrderNumber').text) for cxml in channel_xml]
        metadata.setImageID(ac_id,0 )
        metadata.setImageName(ac_id,0)
        metadata.setPixelsDimensionOrder(DimensionOrder.XYCZT, 0)
        metadata.setPixelsSizeX(PositiveInteger(x), 0)
        metadata.setPixelsSizeY(PositiveInteger(y), 0)
        metadata.setPixelsSizeC(PositiveInteger(c), 0)
        metadata.setPixelsSizeZ(PositiveInteger(1), 0)
        metadata.setPixelsSizeT(PositiveInteger(1), 0)

        metadata.setPixelsPhysicalSizeX(Length(1, units.MICROM), 0)
        metadata.setPixelsPhysicalSizeY(Length(1, units.MICROM), 0)
        metadata.setPixelsPhysicalSizeZ(Length(1, units.MICROM), 0)

        metadata.setPixelsID(ac_id, 0)
        metadata.setPixelsType(PixelType.FLOAT, 0)
        metadata.setPixelsInterleaved(False, 0)

        # metadata.setTiffDataFirstC(NonNegativeInteger(0), 0, 0)
        # metadata.setTiffDataFirstZ(NonNegativeInteger(0), 0, 0)
        # metadata.setTiffDataFirstT(NonNegativeInteger(0), 0, 0)
        print(c)
        for i in range(c):
            metadata.setChannelSamplesPerPixel(PositiveInteger(1), 0, i)
        for cxml in channel_xml:
            cnr = int(cxml.find(ns+'OrderNumber').text)-3
            if cnr >=0:
                name = cxml.find(ns + 'ChannelName').text
                label = cxml.find(ns + 'ChannelLabel')
                if label is None:
                    label = name
                else:
                    label = label.text
                cid = '_'.join([label, name])
                cid = cid.strip('(').strip(')')
                name = name.strip('(').strip(')')
                metadata.setChannelFluor(name, 0, cnr)
                metadata.setChannelName(cid, 0, cnr)
        # for i in range(c):
        #     metadata.setPlaneTheC(NonNegativeInteger(i),0,i)
        #     metadata.setPlaneTheZ(NonNegativeInteger(0), 0, i)
        #     metadata.setPlaneTheT(NonNegativeInteger(0), 0, i)


        return metadata

    else:
        ac_id = imc_acquisition.image_ID
        metadata.setImageID(ac_id, 0)
        metadata.setImageName(ac_id, 0)
        metadata.setPixelsDimensionOrder(DimensionOrder.XYCZT, 0)
        metadata.setPixelsSizeX(PositiveInteger(x), 0)
        metadata.setPixelsSizeY(PositiveInteger(y), 0)
        metadata.setPixelsSizeC(PositiveInteger(c), 0)
        metadata.setPixelsSizeZ(PositiveInteger(1), 0)
        metadata.setPixelsSizeT(PositiveInteger(1), 0)

        metadata.setPixelsPhysicalSizeX(Length(1, units.MICROM), 0)
        metadata.setPixelsPhysicalSizeY(Length(1, units.MICROM), 0)
        metadata.setPixelsPhysicalSizeZ(Length(1, units.MICROM), 0)

        metadata.setPixelsID(ac_id, 0)
        metadata.setPixelsType(PixelType.FLOAT, 0)
        metadata.setPixelsInterleaved(False, 0)

        # metadata.setTiffDataFirstC(NonNegativeInteger(0), 0, 0)
        # metadata.setTiffDataFirstZ(NonNegativeInteger(0), 0, 0)
        # metadata.setTiffDataFirstT(NonNegativeInteger(0), 0, 0)
        print(c)
        for i in range(c):
            metadata.setChannelSamplesPerPixel(PositiveInteger(1), 0, i)
        for cnr, metal, label in zip(range(c), imc_acquisition.channel_metals, imc_acquisition.channel_labels):
            metadata.setChannelFluor(metal, 0, cnr)
            metadata.setChannelName(label, 0, cnr)

        return metadata


def save_ome_tiff(filename, image, metadata):
    reader = ImageReader()
    writer = ImageWriter()
    writer.setMetadataRetrieve(metadata)
    writer.setId(filename)
    nchan = image.getNChannels()
    stack = image.getImageStack()
    print(image.getStackSize())
    for i in range(nchan):
        writer.setSeries(0)
        process = stack.getProcessor(i+1)
        pixels = process.getPixels()
        pixels = DataTools.floatsToBytes(pixels, True)
        writer.saveBytes(i, pixels)
    writer.close()




