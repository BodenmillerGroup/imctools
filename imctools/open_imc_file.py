from __future__ import with_statement, division


from ij import IJ
import ij.gui as gui
from loci.plugins import BF
from ij.io import OpenDialog
from ij import ImageStack
from loci.formats import ImageReader
from loci.formats import MetadataTools
import i5d.Image5D
import i5d


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

    img_data = imc_acquisition.data
    img_channels = imc_acquisition.n_channels
    channel_names = imc_acquisition.channel_names
    channel_labels = imc_acquisition.channel_labels
    ac_id = imc_acquisition.image_ID

    x_vec, y_vec = zip(*[tuple(int(row[i]) for i in [0,1]) for row in img_data])
    max_x = int(max(x_vec) + 1)
    max_y = int(max(y_vec) + 1)
    stack = ImageStack.create(max_x, max_y, img_channels, 32)

    img_processors = [stack.getProcessor(i+1) for i in range(img_channels)]
    for row in img_data:
        x = int(row[0])
        y = int(row[1])
        for col, val in enumerate(row[3:]):
            img_processors[col].putPixelValue(x, y, val)

    file_name = imc_acquisition.original_filename.replace('.mcd','')
    file_name = imc_acquisition.original_filename.replace('.txt', '')
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
                imc_acs = [mcd_parser.get_imc_acquisition(aid) for aid in ac_ids]

    if fn[-4:] == '.txt':
        imc_acs = [imctextacquisitionbase.ImcTextAcquisitionBase(filename=fn)]
        #print('start reshape')
        #img = imc_acs[0]
        #imgstack = img.get_img_stack_cyx()
        #print('end')

    for imc_ac in imc_acs:
        i5d_img = convert_imc_to_image(imc_ac)
        i5d_img.show()

