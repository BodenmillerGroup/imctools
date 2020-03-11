import os
import numpy as np
from tifffile import TiffFile, TiffWriter


def probability_to_uncertainty(filename: str, output_folder: str, basename: str = None, suffix: str = None):
    """
    Resizes an image

    :param fn_stack: The filename of the stack
    :param outfolder: The output folder
    :param basename: The basename to use for the output filename
    :param scalefactor: Factor to scale by
    :return:
    """

    with TiffFile(filename) as tif:
        stack = tif.asarray()

    if len(stack.shape) == 2:
        stack = stack.reshape([1] + list(stack.shape))

    if basename is None:
        basename = os.path.splitext(os.path.basename(filename))[0]

    if suffix is None:
        suffix = "_uncertainty"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    fn = os.path.join(output_folder, basename + suffix + ".tiff")
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
        "/home/anton/Documents/IMC Workshop 2019/Data/IMC_Workshop_2019_preprocessing/data/tiffs/20190919_FluidigmBrCa_SE_s0_p8_r8_a8_ac_ilastik_s2_Probabilities.tiff",
        "/home/anton/Downloads/probability_to_uncertainty",
    )

    print(timeit.default_timer() - tic)
