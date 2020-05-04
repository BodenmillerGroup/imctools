import csv
import glob
import os
from io import StringIO

import pandas as pd

import imctools.io.mcd.constants as const
from imctools.data import Session
from imctools.io.utils import CSV_FILENDING, META_CSV_SUFFIX, SESSION_JSON_SUFFIX

SUFFIX_ACMETA = "_acquisitions" + META_CSV_SUFFIX
COL_MCD_ID = const.ID
COL_AC_ID = const.ACQUISITION_ID
COL_AC_SESSION = "AcSession"
AC_META = "acquisition_metadata"


def export_acquisition_csv(root_folder: str, output_folder: str, output_name=AC_META):
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

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    data.to_csv(os.path.join(output_folder, output_name + CSV_FILENDING), index=False)


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()

    export_acquisition_csv("/home/anton/Downloads/imc_folder/", "/home/anton/Downloads/csv_folder")

    print(timeit.default_timer() - tic)
