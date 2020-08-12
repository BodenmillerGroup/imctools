import os
from pathlib import Path
from typing import Union, Optional

import numpy as np
from tifffile import TiffFile, TiffWriter


def probability_to_uncertainty(
    filename: Union[str, Path], output_folder: Optional[Union[str, Path]] = None, basename: str = None, suffix: str = "_uncertainty"
):
    """Converts probability masks to uncertainties.

    Parameters
    ----------
    filename
        The path to the probability TIFF file.
    output_folder
        Folder to save the images in. By default a sub-folder with the basename image_filename in the image_filename folder.
    basename
        Basename for the output image. Default: image_filename.
    suffix
        Filename suffix.
    """
    if isinstance(filename, str):
        filename = Path(filename)

    if isinstance(output_folder, str):
        output_folder = Path(output_folder)

    with TiffFile(filename) as tif:
        stack = tif.asarray()

    if len(stack.shape) == 2:
        stack = stack.reshape([1] + list(stack.shape))

    if basename is None:
        basename = filename.stem

    if output_folder is not None and not output_folder.exists():
        output_folder.mkdir(parents=True, exist_ok=True)

    if output_folder is not None:
        fn = output_folder / (basename + suffix + ".tiff")
    else:
        fn = filename.parent / (basename + suffix + ".tiff")
    timg = np.max(stack, axis=2)
    if stack.dtype == np.float:
        timg = 1 - timg
    else:
        timg = np.iinfo(stack.dtype).max - timg
    with TiffWriter(fn, imagej=True) as tif:
        tif.save(timg.squeeze())


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()

    probability_to_uncertainty(
        Path("/home/anton/Documents/IMC Workshop 2019/Data/IMC_Workshop_2019_preprocessing/data/tiffs/20190919_FluidigmBrCa_SE_s0_p8_r8_a8_ac_ilastik_s2_Probabilities.tiff"),
        Path("/home/anton/Downloads/probability_to_uncertainty"),
    )

    print(timeit.default_timer() - tic)
