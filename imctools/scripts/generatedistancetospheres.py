#!/usr/bin/env python
import tifffile
import numpy as np
from scipy.ndimage import distance_transform_edt
import imctools.library as lib




def generate_distanceto_spheres(fn_label, cur_label, out_file, bg_label=0):
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

    is_cur = (labels != cur_label)
    is_bg = (labels != bg_label)
    is_other = (is_bg == False) | (is_cur == False)

    with tifffile.TiffWriter(out_file+'.tif', imagej=True) as tif:
        tif.save(lib.distance_transform_wrapper(is_cur).astype(np.float32))
        tif.save(lib.distance_transform_wrapper(is_bg).astype(np.float32))
        tif.save(lib.distance_transform_wrapper(is_other).astype(np.float32))

    return 1


def generate_distanceto_binary(fns_binary, out_file, allinverted=False, addinverted=False):
    """

    :param fn_stack:
    :param fn_label:
    :param outfolder:
    :param basename:
    :param scale:
    :param extend:
    :return:
    """
    
    imgs = list()

    with tifffile.TiffWriter(out_file, imagej=True) as outtif:
        for fn in fns_binary:
            with tifffile.TiffFile(fn) as tif:
                img = tif.asarray()
                if allinverted:
                    img = (img > 0) == False
                else:
                    img = img > 0
                outtif.save(lib.distance_transform_wrapper(img).astype(np.float32))
                if addinverted:
                   outtif.save(lib.distance_transform_wrapper(img == False).astype(np.float32))

    return 1

def generate_binary(fn_label, cur_label, out_file, bg_label=0):
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

    is_cur = labels == cur_label
    is_bg = labels == bg_label
    is_other = (is_bg == False) & (is_cur == False)

    with tifffile.TiffWriter(out_file+'.tif', imagej=True) as tif:
        tif.save(is_cur.astype(np.uint8))
        tif.save(is_bg.astype(np.uint8))
        tif.save(is_other.astype(np.uint8))

    return 1
