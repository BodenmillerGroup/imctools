import logging
import os
from pathlib import Path
from typing import Optional, Sequence, Tuple, Type, Union

import numpy as np
import pandas as pd

from imctools.io.ometiff.ometiffparser import OmeTiffParser

logger = logging.getLogger(__name__)


def get_metals_from_panel(
    panel_csv_file: Optional[Union[str, Path]],
    usedcolumn: str = "ilastik",
    metalcolumn: str = "Metal Tag",
    sort_channels=True,
):
    """Get list of metals from a panel and a boolean column.

    Parameters
    ----------
    panel_csv_file
        Name of the CSV file that contains the channels to be written out.
    metalcolumn
        Column name of the metal names.
    usedcolumn
        Column that should contain booleans (0, 1) if the channel should be used, i.e. "ilastik".
    sort_channels
        Whether to sort channels by mass.
    """
    metals = None

    if panel_csv_file is not None:

        pannel = pd.read_csv(panel_csv_file)
        if pannel.shape[1] > 1:
            selected = pannel[usedcolumn]
            assert selected.any() == 0 or selected.any() == 1, f"Values in 'usedcolumn' column should contain only 0/1"
            metals = [str(n) for s, n in zip(selected, pannel[metalcolumn]) if s]
        else:
            metals = [pannel.columns[0]] + pannel.iloc[:, 0].tolist()

    if sort_channels:
        if metals is not None:

            def mass_from_met(x):
                return int("".join([m for m in x if m.isdigit()])), x

            metals = sorted(metals, key=mass_from_met)

    return metals


def omefile_2_analysisfolder(
    filename: Union[str, Path],
    output_folder: Union[str, Path],
    basename: str,
    panel_csv_file: Optional[Union[str, Path]] = None,
    metalcolumn: str = "Metal Tag",
    usedcolumn: str = "ilastik",
    bigtiff=False,
    sort_channels=True,
    dtype: Optional[Type] = None,
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
    usedcolumn
        Column that should contain booleans (0, 1) if the channel should be used, i.e. "ilastik".
    bigtiff
        Whether to save TIFF files in BigTIFF format.
    sort_channels
        Whether to sort channels by mass.
    dtype
        Output Numpy data type.
    """
    if isinstance(filename, str):
        filename = Path(filename)

    if isinstance(output_folder, str):
        output_folder = Path(output_folder)

    if not output_folder.exists():
        output_folder.mkdir(parents=True, exist_ok=True)

    metals = get_metals_from_panel(panel_csv_file, usedcolumn, metalcolumn, sort_channels)

    ome = OmeTiffParser(filename)
    acquisition_data = ome.get_acquisition_data()

    acquisition_data.save_tiff(
        output_folder / (basename + ".tiff"), names=metals, imagej=True, bigtiff=bigtiff, dtype=dtype
    )

    if metals is not None:
        savenames = metals
    else:
        savenames = [s for s in acquisition_data.channel_names]

    with open(output_folder / (basename + ".csv"), "w") as f:
        for n in savenames:
            f.write(n + "\n")


def omefolder_to_analysisfolder(
    input_folder: Union[str, Path],
    output_folder: Union[str, Path],
    panel_csv_file: Union[str, Path],
    analysis_stacks: Sequence[Tuple[str, str, bool]],
    metalcolumn: str = "Metal Tag",
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
    dtype
        Output numpy dtype
    """
    if isinstance(input_folder, str):
        input_folder = Path(input_folder)
    if isinstance(output_folder, str):
        output_folder = Path(output_folder)

    if not output_folder.exists():
        output_folder.mkdir(parents=True, exist_ok=True)

    for fol in os.listdir(input_folder):
        sub_fol = input_folder / fol
        for img in os.listdir(sub_fol):
            if not img.endswith(".ome.tiff"):
                continue
            basename = img.rstrip(".ome.tiff")
            for (col, suffix, add_sum) in analysis_stacks:
                try:
                    omefile_2_analysisfolder(
                        sub_fol / img,
                        output_folder,
                        basename + suffix,
                        panel_csv_file=panel_csv_file,
                        metalcolumn=metalcolumn,
                        usedcolumn=col,
                        bigtiff=False,
                        dtype=dtype,
                    )
                except:
                    logger.exception("Error in {}".format(img))


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()

    omefile_2_analysisfolder(
        Path(
            "/home/anton/Downloads/imc_folder/20170905_Fluidigmworkshopfinal_SEAJa/20170905_Fluidigmworkshopfinal_SEAJa_s0_a0_ac.ome.tiff"
        ),
        Path("/home/anton/Downloads/analysis_folder"),
        "test",
        panel_csv_file=Path("/home/anton/Downloads/example_panel.csv"),
        metalcolumn="Metal Tag",
        usedcolumn="ilastik",
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
