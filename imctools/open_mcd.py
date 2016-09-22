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


def convert_mcd_to_img(mcd_parser, ac_id):
    """
    Load an MCD and convert it to a image5d Tiff
    :param filename: Filename of the MCD
    :return: an image5d image
    """

    img_data = mcd_parser.get_acquisition_rawdata(ac_id)
    channel_dict = mcd_parser.get_acquisition_channels(ac_id)

    (n_rows, n_channels) = mcd_parser.get_acquisition_dimensions(ac_id)
    buffer_size = len(img_data)
    img_channels = n_channels - 3

    x_vec = [int(img_data[i]) for i in range(0, buffer_size, n_channels)]
    y_vec = [int(img_data[i]) for i in range(1, buffer_size, n_channels)]
    max_x = int(max(x_vec) + 1)
    max_y = int(max(y_vec) + 1)
    stack = ImageStack.create(max_x, max_y, img_channels, 32)

    for cur_chan in range(img_channels):
        cur_proc = stack.getProcessor(cur_chan + 1)
        cur_values = [img_data[i] for i in range(cur_chan + 3, buffer_size, n_channels)]
        for x, y, v in zip(x_vec, y_vec, cur_values):
            cur_proc.putPixelValue(x, y, v)

    file_name = os.path.split(mcd_parser.filename)[1].replace('.mcd','')
    file_name = '_'.join((file_name,ac_id))
    i5d_img = i5d.Image5D(file_name, stack, img_channels, 1, 1)
    for i in range(img_channels):
        (name, label) = channel_dict[i + 3]
        if label is None:
            label = name

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
    bools = [False for aid in ac_ids]
    bools[0] = True
    gd.addCheckboxGroup(len(ac_ids), 1, ac_ids, bools)
    gd.showDialog()
    if not gd.wasCanceled():
        return [aid for aid in ac_ids if gd.getNextBoolean()]
    else:
        return []

if __name__ == '__main__':

    op = OpenDialog('Choose mcd file')
    fn = os.path.join(op.getDirectory(), op.getFileName())

    with mcdparserbase.McdParserBase(fn) as mcd_parser:
        ac_ids = choose_acquisition_dialog(mcd_parser)

        if len(ac_ids) > 0:
            for aid in ac_ids:
                i5d_img = convert_mcd_to_img(mcd_parser, ac_id=aid)
                i5d_img.show()

