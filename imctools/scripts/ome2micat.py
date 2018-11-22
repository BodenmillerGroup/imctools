#!/usr/bin/env python
# Copyright (C) 2018-2019 University of Zurich. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from imctools.io import ometiffparser
import argparse
import os
import shutil
import re


def ome2singletiff(path_ome, outfolder, basename=None, dtype=None):
    """
    Saves the planes of an ome stack as a folder
    :param fn_ome:
    :param outfolder:
    :return:
    """
    ome = ometiffparser.OmetiffParser(path_ome)
    imc_img = ome.get_imc_acquisition()
    if basename is None:
        fn_new = os.path.split(path_ome)[1].rstrip('.ome.tiff') + '_'
    else:
        fn_new = basename
    for label, metal in zip(imc_img.channel_labels, imc_img.channel_metals):
        label = re.sub('[^a-zA-Z0-9]', '-', label)
        new_path = os.path.join(outfolder, fn_new +label+'_'+metal)
        writer = imc_img.get_image_writer(new_path + '.tiff', metals=[metal])
        writer.save_image(mode='imagej', dtype=dtype)

def ome2micatfolder(path_ome, basefolder, path_mask=None, dtype=None):
    """

    :param fn_ome:
    :param basefolder:
    :param fn_mask:
    :return:
    """
    fn = os.path.split(path_ome)[1]
    fn = fn.rstrip('.ome.tiff')
    outfolder = os.path.join(basefolder, fn)
    if not(os.path.exists(outfolder)):
        os.makedirs(outfolder)
    ome2singletiff(path_ome, outfolder,basename='', dtype=dtype)
    if path_mask is not None:
        fn_mask_base = os.path.split(path_mask)[1]
        fn_mask_new = os.path.join(outfolder, fn_mask_base)
        shutil.copy2(path_mask, fn_mask_new)


def omefolder2micatfolder(fol_ome, outfolder, fol_masks=None, mask_suffix=None, dtype=None):
    """

    :param fol_ome:
    :param outfolder:
    :param fol_masks:
    :param mask_suffix:
    :return:
    """
    if mask_suffix is None:
        mask_suffix = '_mask.tiff'

    ome_files = [fn for fn in os.listdir(fol_ome) if fn.endswith('.ome.tiff')]
    if fol_masks is not None:
        fn_masks = [fn for fn in os.listdir(fol_masks) if fn.endswith(mask_suffix)]
    else:
        fn_masks = []

    for fn_ome in ome_files:
        basename_ome = fn_ome.rstrip('.ome.tiff')
        cur_mask = [fn for fn in fn_masks if fn.startswith(basename_ome)]
        if len(cur_mask) > 0:
            path_mask = os.path.join(fol_masks, cur_mask[0])
        else:
            path_mask = None
        path_ome = os.path.join(fol_ome, fn_ome)
        ome2micatfolder(path_ome, outfolder, path_mask=path_mask, dtype=dtype)


if __name__ == "__main__":
    # Setup the command line arguments
    parser = argparse.ArgumentParser(
        description='Convertes an ome folder (or file) to a micat folder', prog='ome2micat')

    parser.add_argument('ome_folder', type=str,
                        help='A folder with ome images or a single ome file')

    parser.add_argument('out_folder', type=str,
                        help='Folder to output the micat folders')

    parser.add_argument('--mask_folder', type=str, default=None,
                        help='Folder containing the masks, or single mask file.')
    parser.add_argument('--mask_suffix', type=str, default='_mask.tiff',
                        help='suffix of the mask tiffs')

    parser.add_argument('--imagetype', type=str, default=None,choices=[None, 'uint16', 'int16', 'float'],
                        help='The output image type')

    # parser.add_argument('--postfix', type=str, default=None,
    #                     help='Postfix to append to the basename.'
    #                     )

    args = parser.parse_args()



    ome_folder = args.ome_folder
    mask_folder = args.mask_folder
    out_folder = args.out_folder
    mask_suffix = args.mask_suffix

    if not(os.path.exists(out_folder)):
        os.mkdir(out_folder)

    if ome_folder.endswith('.ome.tiff'):
        ome2micatfolder(ome_folder, out_folder, mask_folder, dtype=args.imagetype)
    else:
        omefolder2micatfolder(ome_folder, out_folder, mask_folder, mask_suffix=mask_suffix, dtype=args.imagetype)
