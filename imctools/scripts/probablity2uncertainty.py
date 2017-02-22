#!/usr/bin/env python
import tifffile
from scipy import ndimage as ndi
from imctools import library as lib
import argparse
import os
import numpy as np
from skimage import transform


def probability2uncertainty(fn_probability, outfolder, basename=None, suffix=None):
    """
    Resizes an image

    :param fn_stack: The filename of the stack
    :param outfolder: The output folder
    :param basename: The basename to use for the output filename
    :param scalefactor: Factor to scale by
    :return:
    """

    with tifffile.TiffFile(fn_probability) as tif:
        stack = tif.asarray()

    if len(stack.shape) == 2:
        stack = stack.reshape([1]+list(stack.shape))

    if basename is None:
        basename = os.path.splitext(os.path.basename(fn_probability))[0]

    if suffix is None:
        suffix = '_uncertainty'


    fn = os.path.join(outfolder, basename+suffix+'.tiff')
    timg = np.max(stack, 2)
    if stack.dtype == np.float:
        timg = 1-timg
    else:
        timg = np.iinfo(stack.dtype).max-timg
    with tifffile.TiffWriter(fn, imagej=True) as tif:
        tif.save(timg.squeeze())


if __name__ == "__main__":
    # Setup the command line arguments
    parser = argparse.ArgumentParser(
        description='Converts probailiy masks to uncertainties.', prog='probability2uncertainty')

    parser.add_argument('probab_filename', type=str,
                        help='The path to the probablitity tiff')

    parser.add_argument('--out_folder', type=str, default=None,
                        help='Folder to save the images in. Default a subfolder with the basename image_filename in the image_filename folder.')

    parser.add_argument('--basename', type=str, default=None,
                        help='Basename for the output image. Default: image_filename')


    args = parser.parse_args()

    raise Exception('Not implemented')
