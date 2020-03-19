import glob
import logging
import os
import shutil
from typing import Optional

from imctools.io.ometiff.ometiffparser import OmeTiffParser

logger = logging.getLogger(__name__)


def omefile_to_tifffolder(filepath: str, output_folder: str, basename: str = None, dtype: Optional[object] = None):
    """Saves planes of single OME-TIFF file to a folder containing standard TIFF (ImageJ-compatible) files.

    Parameters
    ----------
    filepath
        Path to OME-TIFF input file.
    output_folder
        Output folder.
    basename
        Basename for generated output files.
    dtype
        Output numpy format.
    """
    if not (os.path.exists(output_folder)):
        os.makedirs(output_folder)

    with OmeTiffParser(filepath) as parser:
        acquisition_data = parser.get_acquisition_data()
        acquisition_data.save_tiffs(output_folder, basename=basename, dtype=dtype)


def omefile_to_histocatfolder(
    filepath: str, base_folder: str, mask_file: Optional[str] = None, dtype: Optional[object] = None
):
    """Converts single OME-TIFF file to a folder compatible with HistoCAT software.

    Parameters
    ----------
    filepath
        Path to OME-TIFF input file.
    base_folder
        Base output folder.
    mask_file
        Path to mask file.
    dtype
        Output numpy format.
    """
    basename = os.path.split(filepath)[1].rstrip(".ome.tiff")
    output_folder = os.path.join(base_folder, basename)
    omefile_to_tifffolder(filepath, output_folder, basename="", dtype=dtype)
    if mask_file is not None:
        fn_mask_base = os.path.split(mask_file)[1]
        fn_mask_new = os.path.join(output_folder, fn_mask_base)
        shutil.copy2(mask_file, fn_mask_new)


def omefolder_to_histocatfolder(
    input_folder: str,
    output_folder: str,
    mask_folder: str = None,
    mask_suffix="_mask.tiff",
    dtype: Optional[object] = None,
):
    """Converts all OME-TIFF files in input folder to a folder compatible with HistoCAT software.

    Parameters
    ----------
    input_folder
        Input folder.
    output_folder
        Output folder.
    mask_folder
        Folder containing the masks, or single mask file.
    mask_suffix
        Mask suffix.
    dtype
        Output numpy format.
    """
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
            mask_file = os.path.join(mask_folder, cur_mask[0])
        else:
            mask_file = None
        path_ome = os.path.join(input_folder, fn_ome)
        omefile_to_histocatfolder(path_ome, output_folder, mask_file=mask_file, dtype=dtype)


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()

    omefolder_to_histocatfolder(
        "/home/anton/Downloads/imc_from_mcd", "/home/anton/Downloads/tiff_folder",
    )

    print(timeit.default_timer() - tic)
