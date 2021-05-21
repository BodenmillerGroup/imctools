import glob
import logging
import os
import shutil
from pathlib import Path
from typing import Optional, Union

from imctools.io.ometiff.ometiffparser import OmeTiffParser

logger = logging.getLogger(__name__)


def omefile_to_tifffolder(
    filepath: Union[str, Path], output_folder: Union[str, Path], basename: str = None, dtype: Optional[object] = None
):
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
    if isinstance(output_folder, str):
        output_folder = Path(output_folder)

    if not output_folder.exists():
        output_folder.mkdir(parents=True, exist_ok=True)

    with OmeTiffParser(filepath) as parser:
        acquisition_data = parser.get_acquisition_data()
        acquisition_data.save_tiffs(output_folder, basename=basename, dtype=dtype)


def omefile_to_histocatfolder(
    filepath: Union[str, Path],
    base_folder: Union[str, Path],
    mask_file: Optional[Union[str, Path]] = None,
    dtype: Optional[object] = None,
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
    if isinstance(filepath, str):
        filepath = Path(filepath)

    if isinstance(base_folder, str):
        base_folder = Path(base_folder)

    basename = filepath.name.rstrip(".ome.tiff")
    output_folder = base_folder / basename
    omefile_to_tifffolder(filepath, output_folder, basename="", dtype=dtype)
    if mask_file is not None:
        if isinstance(mask_file, str):
            mask_file = Path(mask_file)
        shutil.copy2(mask_file, output_folder)


def omefolder_to_histocatfolder(
    input_folder: Union[str, Path],
    output_folder: Union[str, Path],
    mask_folder: Optional[Union[str, Path]] = None,
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
    if isinstance(input_folder, Path):
        input_folder = str(input_folder)

    if mask_folder is not None and isinstance(mask_folder, Path):
        mask_folder = str(mask_folder)

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
        Path("/home/anton/Downloads/imc_folder_v2/20191203_HuBMAP_LN"),
        Path("/home/anton/Downloads/tiff_folder"),
        mask_folder="/home/anton/Data/ImcSegmentationPipelineV2/hubmap_processed_v2/masks",
    )

    print(timeit.default_timer() - tic)
