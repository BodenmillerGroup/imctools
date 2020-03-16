import glob
import logging
import os
import shutil

from imctools.io.ometiff.ometiffparser import OmeTiffParser

logger = logging.getLogger(__name__)


def omefile_to_tifffolder(filepath: str, output_folder: str, basename: str = None):
    """
    Converts single OME-TIFF file to a folder containing standard TIFF (ImageJ-compatible) files.
    """
    if not (os.path.exists(output_folder)):
        os.makedirs(output_folder)

    with OmeTiffParser(filepath) as parser:
        acquisition_data = parser.get_acquisition_data()
        acquisition_data.save_tiffs(output_folder, basename=basename)


def omefile_to_histocatfolder(filepath: str, base_folder: str, path_mask: str = None):
    """
    Converts single OME-TIFF file to a folder compatible with HistoCAT software.
    """
    basename = os.path.split(filepath)[1].rstrip(".ome.tiff")
    output_folder = os.path.join(base_folder, basename)
    omefile_to_tifffolder(filepath, output_folder, basename="")
    if path_mask is not None:
        fn_mask_base = os.path.split(path_mask)[1]
        fn_mask_new = os.path.join(output_folder, fn_mask_base)
        shutil.copy2(path_mask, fn_mask_new)


def omefolder_to_histocatfolder(input_folder: str, output_folder: str, mask_folder: str = None, mask_suffix=None):
    """
    Converts all OME-TIFF files in input folder to a folder compatible with HistoCAT software.
    """
    if mask_suffix is None:
        mask_suffix = "_mask.tiff"

    ome_files = [os.path.basename(fn) for fn in glob.glob(os.path.join(input_folder, "*")) if fn.endswith(".ome.tiff")]
    if mask_folder is not None:
        fn_masks = [
            os.path.basename(fn) for fn in glob.glob(os.path.join(mask_folder, "*")) if fn.endswith(mask_suffix)
        ]
    else:
        fn_masks = []

    for fn_ome in ome_files:
        len_suffix = len(".ome.tiff")
        basename_ome = fn_ome[:-len_suffix]
        cur_mask = [fn for fn in fn_masks if fn.startswith(basename_ome)]
        if len(cur_mask) > 0:
            path_mask = os.path.join(mask_folder, cur_mask[0])
        else:
            path_mask = None
        path_ome = os.path.join(input_folder, fn_ome)
        omefile_to_histocatfolder(path_ome, output_folder, path_mask=path_mask)


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()

    omefolder_to_histocatfolder(
        "/home/anton/Downloads/imc_from_mcd", "/home/anton/Downloads/tiff_folder",
    )

    print(timeit.default_timer() - tic)
