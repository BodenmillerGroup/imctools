#!/usr/bin/env python
import tifffile
from scipy import ndimage as ndi
from imctools import library as lib
import argparse
import os
import warnings
from scipy import ndimage as ndi
import numpy as np


def crop_section(fn_stack, outfolder, slice, basename=None):
    """

    :param fn_stack:
    :param outfolder:
    :param basename:
    :param slice:
    :return:
    """
    warnings.warn('''crop_section is deprecated and
                  will not be supported in future versions.
                  Please use the `Crop bb` module from
                  Bodenmillergroup/ImcPluginsCP
                  in CellProfiler!''',
                  DeprecationWarning)
    if basename is None:
       basename = os.path.split(fn_stack)[1].strip('.tif').strip('.tiff')

    with tifffile.TiffFile(fn_stack) as tif:
        stack = tif.asarray()

    if len(stack.shape) == 2:
        stack = stack.reshape([1]+list(stack.shape))

    slice = tuple(slice)

    lib.save_object_stack(outfolder, basename, stack, [slice])

if __name__ == "__main__":
    # Setup the command line arguments
    parser = argparse.ArgumentParser(
        description='Crops a section out of an image.\n'+
                    'The coordinates of the section have to be specified as the coordinates of the upper left'+
                    'corner (x0, y0) as well as the width and height (w, h) of the section in pixels.', prog='cropsection')

    parser.add_argument('image_filename', type=str,
                        help='The path to the image filename. If the image is a stack it needs to be CXY ordered')

    parser.add_argument('section', type=int, nargs=4,
                        help='Specify the section as 4 integers: x0 y0 w h')

    parser.add_argument('--out_folder', type=str, default=None,
                        help='Folder to save the images in. Default a subfolder with the basename image_filename in the image_filename folder.')

    parser.add_argument('--basename', type=str, default=None,
                        help='Basename for the output image. Default: image_filename')

    parser.add_argument('--postfix', type=str, default=None,
                        help='Postfix to append to the basename.'
                        )

    args = parser.parse_args()

    if args.basename is None:
        args.basename = os.path.split(args.image_filename)[1].strip('.tif').strip('.tiff')

    if args.postfix is not None:
        args.basename = args.basename + args.postfix

    if args.out_folder is None:
        args.out_folder = os.path.split(args.image_filename)[0]
        tmpname = os.path.split(args.image_filename)[1].strip('.tif').strip('.tiff')
        args.out_folder = os.path.join(args.out_folder, tmpname)

    if not(os.path.exists(args.out_folder)):
        os.mkdir(args.out_folder)

    if args.randomseed is not None:
        np.random.seed(args.randomseed)

        crop_section(args.image_filename, args.out_folder,
                 args.section, args.basename)
