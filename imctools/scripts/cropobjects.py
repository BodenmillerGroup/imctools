#!/usr/bin/env python
import tifffile
from scipy import ndimage as ndi
from imctools import library as lib
import argparse
import os


def crop_objects(fn_stack, fn_label, outfolder, basename, extend):
    """

    :param fn_stack:
    :param fn_label:
    :param outfolder:
    :param basename:
    :param scale:
    :param extend:
    :return:
    """

    with tifffile.TiffFile(fn_label) as tif:
        labels = tif.asarray()

    with tifffile.TiffFile(fn_stack) as tif:
        stack = tif.asarray()

    if len(stack.shape) == 2:
        stack = stack.reshape([1]+list(stack.shape))
    slices = ndi.find_objects(labels)
    ext_slices = [lib.extend_slice_touple(sl, extend, [stack.shape[1], stack.shape[2]]) for sl in slices]

    lib.save_object_stack(outfolder, basename, stack, ext_slices)

if __name__ == "__main__":
    # Setup the command line arguments
    parser = argparse.ArgumentParser(
        description='Crops objects out of images.', prog='crop_objects')

    parser.add_argument('image_filename', type=str,
                        help='The path to the image filename. If the image is a stack it needs to be CXY ordered')

    parser.add_argument('object_filename', type=str, default=None,
                        help='Filename to the tiff that contains the object masks.')

    parser.add_argument('--out_folder', type=str, default=None,
                        help='Folder to save the images in. Default a subfolder with the basename object_filename in the image_filename folder.')

    parser.add_argument('--extend', type=int, default=0,
                        help='How many pixels to extend around the object.')

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
        tmpname = os.path.split(args.object_filename)[1].strip('.tif').strip('.tiff')
        args.out_folder = os.path.join(args.out_folder, tmpname)

    if not(os.path.exists(args.out_folder)):
        os.mkdir(args.out_folder)

    crop_objects(args.image_filename, args.object_filename, args.out_folder,
                 args.basename, args.extend)