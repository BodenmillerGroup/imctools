from __future__ import with_statement, division

from ij import IJ
import ij.gui as gui
from ij.io import OpenDialog

import os
import sys
imctool_dir = os.path.join(IJ.getDirectory('plugins'),'imctools')
sys.path.append(os.path.realpath(imctool_dir))

import imctools.imagej.library as lib
print('test')
import imctools.io.mcdparserbase as mcdparserbase
import imctools.io.txtparserbase as txtparserbase


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


print('test2')
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
    imc_acs = [txtparserbase.TxtParserBase(filename=fn).get_imc_acquisition()]

for imc_ac in imc_acs:
        i5d_img = lib.convert_imc_to_image(imc_ac)

        i5d_img.show()
        meta = lib.generate_ome_fromimc(imc_ac)
        name = os.path.basename(imc_ac.original_file)

        name = name.strip('.mcd').strip('.txt')

        if imc_ac.origin == 'mcd':
            name = '_'.join([name,imc_ac.image_ID])
        path = os.path.split(imc_ac.original_file)[0]

        fname = os.path.join(path, name+'.ome.tiff')
        if not(os.path.exists(fname)):
            lib.save_ome_tiff(fname, i5d_img, meta)

        del imc_ac


