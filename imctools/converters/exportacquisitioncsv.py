import os

import pandas as pd

import imctools.io.mcd.constants as const
from imctools.io.utils import CSV_FILENDING, META_CSV_SUFFIX

SUFFIX_ACMETA = "_acquisitions" + META_CSV_SUFFIX
COL_MCD_ID = const.ID
COL_AC_ID = const.ACQUISITION_ID
COL_AC_SESSION = "AcSession"
AC_META = "acquisition_metadata"


def _read_and_concat(ome_folder: str, suffix: str, idname: str):
    ac_names = os.listdir(ome_folder)
    dat = pd.concat(
        [pd.read_csv(os.path.join(ome_folder, a, a + suffix)) for a in ac_names], keys=ac_names, names=[COL_AC_SESSION]
    )
    dat = dat.reset_index(COL_AC_SESSION, drop=False)
    dat = dat.rename(columns={COL_MCD_ID: idname})
    return dat


def read_ac_meta(ome_folder: str):
    ac_meta = _read_and_concat(ome_folder, SUFFIX_ACMETA, COL_AC_ID)
    return ac_meta


def export_acquisition_csv(ome_folder: str, output_folder: str, output_name=AC_META):
    """Reads all the acquisition metadata from the ome folders and concatenates them to a csv that contains all the metadata.

    Parameters
    ----------
    ome_folder
        The path to the folders containing the OME-TIFFs.
    output_folder
        Folder where the metadata CSV file should be stored in.
    output_name
        Filename of the acquisition metadata CSV file.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    dat_meta = read_ac_meta(ome_folder)
    dat_meta.to_csv(os.path.join(output_folder, output_name + CSV_FILENDING), index=False)


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()

    export_acquisition_csv("/home/anton/Downloads/imc_folder/", "/home/anton/Downloads/csv_folder")

    print(timeit.default_timer() - tic)
