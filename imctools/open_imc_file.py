from __future__ import with_statement, division

from ij import IJ
import ij.gui as gui
import ij.process as process
from loci.plugins import BF
from ij.io import OpenDialog
from ij import ImageStack
from loci.formats import ImageReader
from loci.formats import MetadataTools
import i5d.Image5D
import i5d

from java.lang import Class
from jarray import array


import os
import sys
imctool_dir = os.path.join(IJ.getDirectory('plugins'),'imctools')
sys.path.append(os.path.realpath(imctool_dir))

from io import mcdparserbase
from io import imctextacquisitionbase


def convert_imc_to_image(imc_acquisition):
    """
    Load an MCD and convert it to a image5d Tiff
    :param filename: Filename of the MCD
    :return: an image5d image
    """
    ac_id = imc_acquisition.image_ID
    print('Contstruct image from data: %s' %ac_id)
    img_data = imc_acquisition.get_img_stack_cxy()
    img_channels = imc_acquisition.n_channels
    channel_names = imc_acquisition.channel_names
    channel_labels = imc_acquisition.channel_labels

    max_x = len(img_data[0])
    max_y = len(img_data[0][0])
    stack = ImageStack(max_x, max_y)

    print('Add planes to stack:')
    for i in range(img_channels):
        cur_proc = process.FloatProcessor(img_data[i])
        stack.addSlice(cur_proc)

    file_name = imc_acquisition.original_filename.replace('.mcd','')
    file_name = file_name.replace('.txt', '')
    description = imc_acquisition.image_description
    if description is not None:
        file_name = '_'.join((file_name,'a'+ac_id, 'd'+description))
    else:
        file_name = '_'.join((file_name, 'a' + ac_id))

    i5d_img = i5d.Image5D(file_name, stack, img_channels, 1, 1)
    for i in range(img_channels):
        name = channel_names[i]
        if channel_labels is None:
            cid = name
        else:
            label = channel_labels[i]
            cid = label + '_' + name
        i5d_img.getChannelCalibration(i + 1).setLabel(str(cid))

    i5d_img.setDefaultColors()
    print('finished image: %s' %ac_id)

    return i5d_img


def choose_acquisition_dialog(mcd_parser):
    """

    :param mcd_parser:
    :return:
    """
    gd = gui.GenericDialog('Choose Acquisition')

    ac_ids = mcd_parser.acquisition_ids

    descriptions = [mcd_parser.get_acquisition_description(aid, default='Acquisition '+aid) for aid in ac_ids]
    bools = [False for aid in ac_ids]
    bools[0] = True
    gd.addCheckboxGroup(len(ac_ids), 2, descriptions, bools)
    gd.showDialog()
    if not gd.wasCanceled():
        return [aid for aid in ac_ids if gd.getNextBoolean()]
    else:
        return []

if __name__ == '__main__':
    op = OpenDialog('Choose mcd file')
    fn = os.path.join(op.getDirectory(), op.getFileName())

    if fn[-4:] == '.mcd':
        with mcdparserbase.McdParserBase(fn) as mcd_parser:
            ac_ids = choose_acquisition_dialog(mcd_parser)
            if len(ac_ids) > 0:
                print('Load mcd acquisition: %s' %ac_ids)
                imc_acs = [mcd_parser.get_imc_acquisition(aid) for aid in ac_ids]

    if fn[-4:] == '.txt':
        print('Load txt acquisition:')
        imc_acs = [imctextacquisitionbase.ImcTextAcquisitionBase(filename=fn)]

    for imc_ac in imc_acs:
        i5d_img = convert_imc_to_image(imc_ac)
        del imc_ac
        i5d_img.show()

