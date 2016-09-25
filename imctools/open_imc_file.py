from __future__ import with_statement, division

from ij import IJ
import ij.gui as gui
from ij.io import OpenDialog

from imctools.imagej import library as lib

import os
import sys
imctool_dir = os.path.join(IJ.getDirectory('plugins'),'imctools')
sys.path.append(os.path.realpath(imctool_dir))

from io import mcdparserbase
from io import imctextacquisitionbase


def choose_acquisition_dialog(mcd_parser):
    """

    :param mcd_parser:
    :return:
    """
    gd = gui.GenericDialog('Choose Acquisition')

    ac_ids = mcd_parser.acquisition_ids

    descriptions = [mcd_parser.get_acquisition_description(aid, default='Acquisition '+aid) for aid in ac_ids]
    bools = [False for aid in ac_ids]
    bools[0] = True
    gd.addCheckboxGroup(len(ac_ids), 2, descriptions, bools)
    gd.showDialog()
    if not gd.wasCanceled():
        return [aid for aid in ac_ids if gd.getNextBoolean()]
    else:
        return []

if __name__ == '__main__':
    op = OpenDialog('Choose mcd file')
    fn = os.path.join(op.getDirectory(), op.getFileName())

    if fn[-4:] == '.mcd':
        with mcdparserbase.McdParserBase(fn) as mcd_parser:
            ac_ids = choose_acquisition_dialog(mcd_parser)
            if len(ac_ids) > 0:
                print('Load mcd acquisition: %s' %ac_ids)
                imc_acs = [mcd_parser.get_imc_acquisition(aid) for aid in ac_ids]

    if fn[-4:] == '.txt':
        print('Load txt acquisition:')
        imc_acs = [imctextacquisitionbase.ImcTextAcquisitionBase(filename=fn)]

    for imc_ac in imc_acs:
        i5d_img = lib.convert_imc_to_image(imc_ac)

        i5d_img.show()
        meta = lib.generate_ome_fromimc(imc_ac)
        print(meta.dumpXML())
        #lib.save_ome_tiff(i5d_img, meta)

        del imc_ac


