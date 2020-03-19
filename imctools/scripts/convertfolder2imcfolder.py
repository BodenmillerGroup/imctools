#! /usr/bin/env python
import warnings

from imctools.io.mcdparser import McdParser
from imctools.io.txtparser import TxtParser
from imctools.external import temporarydirectory
from imctools.io.imcfolderwriter import ImcFolderWriter
import os
import zipfile
import argparse
import logging

TXT_FILENDING = ".txt"
MCD_FILENDING = ".mcd"
ZIP_FILENDING = ".zip"
SCHEMA_FILENDING = ".schema"

def convert_folder2imcfolder(fol, out_folder, dozip=True):
    """
    Convert a folder containing IMC acquisitions
    (mcd and tiff)
    to a zipfolder containing standardized names files.
    """
    warnings.warn(
        "imctools 1.x is deprecated, please migrate to version 2.x", DeprecationWarning
    )

    if fol.endswith(ZIP_FILENDING):
        tmpdir = temporarydirectory.TemporaryDirectory()
        with zipfile.ZipFile(fol, allowZip64=True) as zipf:
            zipf.extractall(tmpdir.name)
        in_fol = tmpdir.name
        istmp = True
    else:
        in_fol = fol
        istmp = False

    try:
        files = [
            os.path.join(root, fn)
            for root, dirs, files in os.walk(in_fol)
            for fn in files
        ]
        mcd_files = [f for f in files if f.endswith(MCD_FILENDING)]
        assert len(mcd_files) == 1
        schema_files = [f for f in files if f.endswith(SCHEMA_FILENDING)]
        if len(schema_files) > 0:
            schema_file = schema_files[0]
        else:
            schema_file = None
        try:
            mcd = McdParser(mcd_files[0])
        except:
            if schema_file is not None:
                logging.exception(
                    "Mcd File corrupted, trying to rescue with schema file"
                )
                mcd = McdParser(mcd_files[0], metafilename=schema_file)
            else:
                raise
        mcd_acs = mcd.get_all_imcacquistions()

        txt_acids = {_txtfn_to_ac(f): f for f in files if f.endswith(TXT_FILENDING)}
        mcd_acids = set(m.image_ID for m in mcd_acs)
        txtonly_acs = set(txt_acids.keys()).difference(mcd_acids)
        for txta in txtonly_acs:
            print("Using TXT file for acquisition: " + txta)
            try:
                mcd_acs.append(TxtParser(txt_acids[txta]).get_imc_acquisition())
            except:
                print("TXT file was also corrupted.")
        imc_fol = ImcFolderWriter(out_folder, mcddata=mcd, imcacquisitions=mcd_acs)
        imc_fol.write_imc_folder(zipfolder=dozip)
        if istmp:
            tmpdir.cleanup()
    finally:
        if istmp:
            tmpdir.cleanup()


def _txtfn_to_ac(fn):
    return TxtParser._txtfn_to_ac(fn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert a folder or zip of IMC rawdat"
        + " (.mcd+.txt) into an IMC folder.",
        prog="fol2imcfol",
        usage="%(prog)s folder_path [options]",
    )
    parser.add_argument(
        "folder_path",
        metavar="folder_path",
        type=str,
        help="The path to the folder/zip archive containing the IMC rawdata",
    )
    parser.add_argument(
        "--out_folder",
        metavar="out_folder",
        type=str,
        default="",
        help="Path to the output folder",
    )

    args = parser.parse_args()
    in_fol = args.folder_path
    out_fol = args.out_folder
    if out_fol == "":
        out_fol = os.path.split(in_fol)[0]
    convert_folder2imcfolder(in_fol, out_fol)
