import logging
import os
from typing import Sequence, Tuple, Type

import numpy as np
import pandas as pd

from imctools.io.ometiff.ometiffparser import OmeTiffParser

logger = logging.getLogger(__name__)


def omefile_2_analysisfolder(
    filename: str,
    output_folder: str,
    basename: str,
    panel_csv_file: str = None,
    metalcolumn: str = "Metal Tag",
    masscolumn: str = None,
    usedcolumn: str = None,
    add_sum=False,
    bigtiff=False,
    sort_channels=True,
    dtype: Type = None,
):
    """Converts single OME-TIFF file to folder compatible with IMC segmentation pipeline.

    Parameters
    ----------
    filename
        Path to input OME-TIFF file.
    output_folder
        Output folder.
    basename
        Basename of the acquisition.
    panel_csv_file
        Name of the CSV file that contains the channels to be written out.
    metalcolumn
        Column name of the metal names.
    masscolumn
        Column name of the mass names. If provided the metal column will be ignored.
    usedcolumn
        Column that should contain booleans (0, 1) if the channel should be used, i.e. "ilastik".
    add_sum
        Add the sum of the data as the first layer.
    bigtiff
        Whether to save TIFF files in BigTIFF format.
    sort_channels
        Whether to sort channels by mass.
    dtype
        Output Numpy data type.
    """
    metals = None
    masses = None

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    outname = os.path.join(output_folder, basename)
    if panel_csv_file is not None:

        pannel = pd.read_csv(panel_csv_file)
        if pannel.shape[1] > 1:
            selected = pannel[usedcolumn]
            if masscolumn is None:
                metalcolumn = metalcolumn
                metals = [str(n) for s, n in zip(selected, pannel[metalcolumn]) if s]
            else:
                masses = [str(n) for s, n in zip(selected, pannel[masscolumn]) if s]
        else:
            metals = [pannel.columns[0]] + pannel.iloc[:, 0].tolist()
    ome = OmeTiffParser(filename)
    acquisition_data = ome.get_acquisition_data()

    if sort_channels:
        if metals is not None:

            def mass_from_met(x):
                return "".join([m for m in x if m.isdigit()]), x

            metals = sorted(metals, key=mass_from_met)
        if masses is not None:
            masses = sorted(masses)

    acquisition_data.save_tiff(
        outname + ".tiff", names=metals, masses=masses, add_sum=add_sum, imagej=True, bigtiff=bigtiff, dtype=dtype
    )

    if masses is not None:
        savenames = masses
    elif metals is not None:
        savenames = metals
    else:
        savenames = [s for s in acquisition_data.channel_names]

    if add_sum:
        savenames = ["sum"] + savenames

    with open(outname + ".csv", "w") as f:
        for n in savenames:
            f.write(n + "\n")


def omefolder_to_analysisfolder(
    input_folder: str,
    output_folder: str,
    panel_csv_file: str,
    analysis_stacks: Sequence[Tuple[str, str, bool]],
    metalcolumn: str = "Metal Tag",
    masscolumn: str = None,
    dtype=np.uint16,
):
    """Convert OME tiffs to analysis tiffs that are more compatible with tools. A CSV with a boolean column can be used to select subsets of channels or metals from the stack. The channels of the tiff will have the same order as in the csv.'

    Parameters
    ----------
    input_folder
        Input folder
    output_folder
        Output folder
    panel_csv_file
        Name of the CSV file that contains the channels to be written out.
    analysis_stacks
        Array of analysis stack definitions in a tuple format (column, suffix, add_sum).
    metalcolumn
        Column name of the metal names.
    masscolumn
        Column name of the mass names. If provided the metal column will be ignored.
    dtype
        Output numpy dtype
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for fol in os.listdir(input_folder):
        sub_fol = os.path.join(input_folder, fol)
        for img in os.listdir(sub_fol):
            if not img.endswith(".ome.tiff"):
                continue
            basename = img.rstrip(".ome.tiff")
            for (col, suffix, add_sum) in analysis_stacks:
                try:
                    omefile_2_analysisfolder(
                        os.path.join(sub_fol, img),
                        output_folder,
                        basename + suffix,
                        panel_csv_file=panel_csv_file,
                        metalcolumn=metalcolumn,
                        masscolumn=masscolumn,
                        usedcolumn=col,
                        add_sum=add_sum,
                        bigtiff=False,
                        dtype=dtype,
                    )
                except:
                    logger.exception("Error in {}".format(img))


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()

    omefile_2_analysisfolder(
        "/home/anton/Downloads/imc_folder/20170905_Fluidigmworkshopfinal_SEAJa/20170905_Fluidigmworkshopfinal_SEAJa_s0_a0_ac.ome.tiff",
        "/home/anton/Downloads/analysis_folder",
        "test",
        panel_csv_file="/home/anton/Downloads/example_panel.csv",
        metalcolumn="Metal Tag",
        usedcolumn="ilastik",
        add_sum=True,
    )

    # omefolder_to_analysisfolder(
    #     "/home/anton/Downloads/imc_folder",
    #     "/home/anton/Downloads/analysis_folder",
    #     "/home/anton/Downloads/example_panel.csv",
    #     [
    #         ("ilastik", "_ilastik", True),
    #         ("full", "_full", False)
    #     ],
    #     metalcolumn="Metal Tag",
    # )

    print(timeit.default_timer() - tic)
