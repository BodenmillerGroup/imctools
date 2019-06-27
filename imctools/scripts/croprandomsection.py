#!/usr/bin/env python
import tifffile
from scipy import ndimage as ndi
from imctools import library as lib
import argparse
import os
import warnings
from scipy import ndimage as ndi
import numpy as np


def crop_random_section(fn_stack, outfolder, basename, size, random_seed=None):
    """

    :param fn_stack:
    :param outfolder:
    :param basename:
    :param scale:
    :param extend:
    :return:
    """
    warnings.warn('''crop_random_section is deprecated and
                  will not be supported in future versions.
                  Please use the `Crop bb` module from
                  Bodenmillergroup/ImcPluginsCP
                  in CellProfiler!''',
                  DeprecationWarning)

    with tifffile.TiffFile(fn_stack) as tif:
        stack = tif.asarray()

    if len(stack.shape) == 2:
        stack = stack.reshape([1]+list(stack.shape))

    slice = []
    xmax = stack.shape[1]

    if random_seed is not None:
        np.random.seed(random_seed)
    if xmax > size:
        x_start = np.random.randint(0,xmax-size)
        slice.append(np.s_[x_start:(x_start+size)])
    else:
        slice.append(np.s_[0:xmax])

    ymax = stack.shape[2]
    if ymax > size:
        x_start = np.random.randint(0,ymax-size)
        slice.append(np.s_[x_start:(x_start+size)])
    else:
        slice.append(np.s_[0:ymax])

    slice = tuple(slice)

    lib.save_object_stack(outfolder, basename, stack, [slice])

if __name__ == "__main__":
    # Setup the command line arguments
    parser = argparse.ArgumentParser(
        description='Crops a random section out of an image.', prog='croprandomsection')

    parser.add_argument('image_filename', type=str,
                        help='The path to the image filename. If the image is a stack it needs to be CXY ordered')

    parser.add_argument('size', type=int, default=100,
                        help='How many pixels should the side of the square of the cutout be. If the image is smaller')

    parser.add_argument('--out_folder', type=str, default=None,
                        help='Folder to save the images in. Default a subfolder with the basename image_filename in the image_filename folder.')

    parser.add_argument('--basename', type=str, default=None,
                        help='Basename for the output image. Default: image_filename')

    parser.add_argument('--postfix', type=str, default=None,
                        help='Postfix to append to the basename.'
                        )

    parser.add_argument('--randomseed', type=float, default=None,
                        help='Random seed. Not set per default.'
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

    crop_random_section(args.image_filename, args.out_folder,
                 args.basename, args.size)
