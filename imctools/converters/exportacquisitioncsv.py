import csv
import glob
import os
from io import StringIO
from pathlib import Path
from typing import Union

import pandas as pd

import imctools.io.mcd.constants as const
from imctools.data import Session
from imctools.io.utils import CSV_FILENDING, META_CSV_SUFFIX, SESSION_JSON_SUFFIX

SUFFIX_ACMETA = "_acquisitions" + META_CSV_SUFFIX
COL_MCD_ID = const.ID
COL_AC_ID = const.ACQUISITION_ID
COL_AC_SESSION = "AcSession"
AC_META = "acquisition_metadata"


def export_acquisition_csv(root_folder: Union[str, Path], output_folder: Union[str, Path], output_name=AC_META):
    """Export CSV file with merged acquisition metadata from all session subfolders.

    Parameters
    ----------
    root_folder
        The path to the folders containing the OME-TIFFs.
    output_folder
        Folder where the metadata CSV file should be stored in.
    output_name
        Filename of the acquisition metadata CSV file.
    """
    if isinstance(root_folder, Path):
        root_folder = str(root_folder)
    if isinstance(output_folder, str):
        output_folder = Path(output_folder)
    ac_names = os.listdir(root_folder)
    session_files = glob.glob(os.path.join(root_folder, f"*/*{SESSION_JSON_SUFFIX}"), recursive=True)
    if len(session_files) == 0:
        raise ValueError("No session JSON files available.")

    stack = []
    for session_file in session_files:
        session = Session.load(session_file)
        acquisitions = [v.get_csv_dict() for v in session.acquisitions.values()]
        cols = acquisitions[0].keys()
        with StringIO() as buffer:
            writer = csv.DictWriter(buffer, sorted(cols))
            writer.writeheader()
            writer.writerows(acquisitions)
            buffer.seek(0)
            stack.append(pd.read_csv(buffer))
    data = pd.concat(stack, keys=ac_names, names=[COL_AC_SESSION])
    data = data.reset_index(COL_AC_SESSION, drop=False)
    data.rename(columns={COL_MCD_ID: COL_AC_ID})

    if not output_folder.exists():
        output_folder.mkdir(parents=True, exist_ok=True)

    data.to_csv(output_folder / (output_name + CSV_FILENDING), index=False)


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()

    export_acquisition_csv(Path("/home/anton/Downloads/imc_folder/"), Path("/home/anton/Downloads/csv_folder"))

    print(timeit.default_timer() - tic)
