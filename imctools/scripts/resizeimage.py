#!/usr/bin/env python
import tifffile
from scipy import ndimage as ndi
from imctools import library as lib
import argparse
import os
import numpy as np
from skimage import transform


def resize_image(fn_stack, outfolder, basename, scalefactor):
    """
    Resizes an image

    :param fn_stack: The filename of the stack
    :param outfolder: The output folder
    :param basename: The basename to use for the output filename
    :param scalefactor: Factor to scale by
    :return:
    """

    with tifffile.TiffFile(fn_stack) as tif:
        stack = tif.asarray()

    if len(stack.shape) == 2:
        stack = stack.reshape([1]+list(stack.shape))

    fn = os.path.join(outfolder, basename+'.tiff')
    with tifffile.TiffWriter(fn, imagej=True) as tif:
        for chan in range(stack.shape[0]):
            timg = stack[chan, :, :]
            timg = transform.rescale(timg, scalefactor, preserve_range=True, order=3)
            tif.save(timg.astype(np.float32).squeeze())

if __name__ == "__main__":
    # Setup the command line arguments
    parser = argparse.ArgumentParser(
        description='Scales image by a factor.', prog='scaleimage')

    parser.add_argument('image_filename', type=str,
                        help='The path to the image filename. If the image is a stack it needs to be CXY ordered')

    parser.add_argument('scalingfactor', type=float, default=2,
                        help='How much should the image be scaled.')

    parser.add_argument('--out_folder', type=str, default=None,
                        help='Folder to save the images in. Default a subfolder with the basename image_filename in the image_filename folder.')

    parser.add_argument('--basename', type=str, default=None,
                        help='Basename for the output image. Default: image_filename')

    # parser.add_argument('--postfix', type=str, default=None,
    #                     help='Postfix to append to the basename.'
    #                     )

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

    resize_image(args.image_filename, args.out_folder,
                 args.basename, args.scalingfactor)