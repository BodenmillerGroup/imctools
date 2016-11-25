#!/usr/bin/env python
from imctools.io import ometiffparser
import argparse
import os
import shutil


def ome2singletiff(path_ome, outfolder):
    """
    Saves the planes of an ome stack as a folder
    :param fn_ome:
    :param outfolder:
    :return:
    """
    ome = ometiffparser.OmetiffParser(path_ome)
    imc_img = ome.get_imc_acquisition()
    fn_new = os.path.split(path_ome)[1].rstrip('.ome.tiff')
    for label, metal in zip(imc_img.channel_labels, imc_img.channel_metals):
        new_path = os.path.join(outfolder, fn_new+'_'+label+'_'+metal+'.tiff')
        writer = imc_img.get_image_writer(new_path + '.tiff', metals=metal)
        writer.save_image(mode='imagej')

def ome2micatfolder(path_ome, basefolder, path_mask=None):
    """

    :param fn_ome:
    :param basefolder:
    :param fn_mask:
    :return:
    """
    fn = os.path.split(path_ome)[1]
    fn = fn.rstrip('.ome.tiff')
    outfolder = os.path.join(basefolder, fn)
    os.makedirs(outfolder)
    ome2singletiff(path_ome, outfolder)
    if path_mask is not None:
        fn_mask_base = os.path.split(path_mask)[1]
        fn_mask_new = os.path.join(outfolder, fn_mask_base)
        shutil.copy2(path_mask, fn_mask_new)


def omefolder2micatfolder(fol_ome, outfolder, fol_masks=None, mask_suffix=None):
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
        ome2micatfolder(path_ome, outfolder, path_mask=path_mask)


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

    # parser.add_argument('--postfix', type=str, default=None,
    #                     help='Postfix to append to the basename.'
    #                     )

    args = parser.parse_args()



    ome_folder = args.ome_folder
    mask_folder = args.mask_folder
    out_folder = args.out_folder

    if not(os.path.exists(out_folder)):
        os.mkdir(out_folder)

    if ome_folder.endswith('.ome.tiff'):
        ome2micatfolder(ome_folder, out_folder, mask_folder)
    else:
        omefolder2micatfolder(ome_folder, out_folder, mask_folder)