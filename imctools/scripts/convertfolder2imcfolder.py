#! /usr/bin/env python
# Copyright (C) 2018-2019 University of Zurich. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
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
SCHEMA_FILENDING = '.schema'

def unzip_dataset(dataset):
    """
    Creates tmp folder where dataset
    gets unzipped.
    Returns location of unzipped folder.
    Raise Exception if fails.
    """

    tmpdir = temporarydirectory.TemporaryDirectory()
    with zipfile.ZipFile(dataset) as zipf:
        zipf.extractall(tmpdir.name)
    return (tmpdir.name,tmpdir)

def convert_folder2imcfolder(dataset_ref, out_folder, dozip=True):
    """
    Convert a folder containing IMC acquisitions
    (mcd and tiff)
    to a zipfolder containing standardized names files.
    Note: `dozip` should be dropped.
    """
    
    if fol.endswith(ZIP_FILENDING):
        try:
            (dataset_loc,tmpdir) = _unzip_dataset(dataset_ref)
            return _convert2imc_folder(dataset_loc)
        finally:
            tmpdir.cleanup()
    else:
        return _convert2imc_folder(dataset_ref)

def _convert2imc_folder(dataset_loc):
    """
    """
    files = [os.path.join(root, fn) for root, dirs, files in os.walk(dataset_loc) for fn in files]
    mcd_files = [f for f in files
                 if f.endswith(MCD_FILENDING)]

    assert(len(mcd_files) == 1), "FATAL: Found more than 1 {0} files".format(MCD_FILENDING)

    schema_files = [f for f in files if f.endswith(SCHEMA_FILENDING)]
    if len(schema_files) > 0:
        schema_file = schema_files[0]
    else:
            schema_file = None
        mcd = McdParser(mcd_files[0], metafilename=schema_file)
        txt_acids = {_txtfn_to_ac(f): f
                   for f in files if f.endswith(TXT_FILENDING)}
        mcd_acs = mcd.get_all_imcacquistions()
        mcd_acids = set(m.image_ID for m in mcd_acs)
        txtonly_acs = set(txt_acids.keys()).difference(mcd_acids)
        for txta in txtonly_acs:
            print('Using TXT file for acquisition: '+txta)
            try:
                mcd_acs.append(
                    TxtParser(
                     txt_acids[txta]).get_imc_acquisition())
            except:
                print('TXT file was also corrupted.')
        imc_fol = ImcFolderWriter(out_folder,
                        mcddata=mcd,
                 imcacquisitions=mcd_acs)
        imc_fol.write_imc_folder(zipfolder=dozip)
        if istmp:
            tmpdir.cleanup()
    finally:
        if istmp:
            tmpdir.cleanup()


def _txtfn_to_ac(fn):
    return TxtParser.txtfn_to_ac(fn)

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
        
