#!/usr/bin/env python
import tifffile
import numpy as np
from scipy.ndimage import distance_transform_edt

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

    is_cur = labels == cur_label
    is_bg = labels == bg_label
    is_other = (is_bg == False) & (is_cur == False)

    with tifffile.TiffWriter(out_file+'.tif', imagej=True) as tif:
        tif.save(distance_transform_edt(is_cur).astype(np.float32))
        tif.save(distance_transform_edt(is_bg).astype(np.float32))
        tif.save(distance_transform_edt(is_other).astype(np.float32))

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