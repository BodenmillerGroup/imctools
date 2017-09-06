#! /usr/bin/env python
from imctools.io.mcdparser import McdParser
from imctools.io.txtparser import TxtParser
from imctools.external import temporarydirectory
from imctools.io.imcfolderwriter import ImcFolderWriter
import os
import zipfile
import argparse
TXT_FILENDING = '.txt'
MCD_FILENDING = '.mcd'
ZIP_FILENDING = '.zip'

def convert_folder2imcfolder(fol, out_folder):
    """
    Convert a folder containing IMC acquisitions
    (mcd and tiff)
    to a zipfolder containing standardized names files.
    """
    if fol.endswith(ZIP_FILENDING):
        tmpdir = temporarydirectory.TemporaryDirectory()
        with zipfile.ZipFile(fol) as zipf:
            zipf.extractall(tmpdir.name)
        in_fol = tmpdir.name
        istmp = True
    else:
        in_fol = fol
        istmp = False
    
    try:
        files = os.listdir(in_fol)
        mcd_files = [f for f in files
                     if f.endswith(MCD_FILENDING)]
        assert(len(mcd_files) == 1)

        mcd = McdParser(os.path.join(in_fol, mcd_files[0]))
        txt_acids = {_txtfn_to_ac(f): f
                   for f in files if f.endswith(TXT_FILENDING)}
        mcd_acs = mcd.get_all_imcacquistions()
        mcd_acids = set(m.image_ID for m in mcd_acs)
        txtonly_acs = set(txt_acids.keys()).difference(mcd_acids)
        for txta in txtonly_acs:
            print('Using TXT file for acquisition: '+txta)
            mcd_acs.append(
                TxtParser(
                    os.path.join(in_fol, txt_acids[txta])).get_imc_acquisition())
        imc_fol = ImcFolderWriter(out_folder,
                        mcddata=mcd,
                 imcacquisitions=mcd_acs)
        imc_fol.write_imc_folder()
        if istmp:
            tmpdir.cleanup()
    finally:
        if istmp:
            tmpdir.cleanup()


def _txtfn_to_ac(fn):
    return TxtParser._txtfn_to_ac(fn)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Convert a folder or zip of IMC rawdat'+
        ' (.mcd+.txt) into an IMC folder.',
        prog='fol2imcfol',
        usage='%(prog)s folder_path [options]')
    parser.add_argument('folder_path', metavar='folder_path',
                        type=str,
                        help='The path to the folder/zip archive containing the IMC rawdata')
    parser.add_argument('--out_folder', metavar='out_folder',
                        type=str,
                        default='',
                        help='Path to the output folder')
    
    args = parser.parse_args()
    in_fol = args.folder_path
    out_fol = args.out_folder
    if out_fol == '':
        out_fol = os.path.split(in_fol)[0]
    convert_folder2imcfolder(in_fol, out_fol)
        
