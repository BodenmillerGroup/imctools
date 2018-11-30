import os
import re
import urllib.request
import logging

from imctools.scripts import convertfolder2imcfolder
from imctools.scripts import ometiff2analysis
from imctools.scripts import imc2tiff
from imctools.scripts import ome2micat
from imctools.scripts import probablity2uncertainty
from imctools.scripts import convertfolder2imcfolder
from imctools.scripts import exportacquisitioncsv
import imctools.scripts.pipeline.configuration as c

logging.basicConfig(level=logging.ERROR)

def initialize_folderstructure(config):
    """
    Initialize the folderstructure acording to the configuraiton.
    :param config: The imcepipeline configuration object.
    :returns None
	"""
    basefol = config[c.OUTPUTFOLDERS][c.OUTPUTFOLDERS_BASE]
    subfols_dict = config[c.OUTPUTFOLDERS][c.OUTPUTFOLDERS_SUBFOLDERS]
    subfols = subfols_dict.values()
    for fol in subfols:
        fol = os.path.join(basefol, fol)
        if not os.path.exists(fol):
            os.makedirs(fol)

def convert_rawzip_to_ome(config):
    """
    Converts the rawdata (zipped acquisitions with 1 mcd and all .txt files)
    to folders containing the images as .ome tiffs.
    :param config: The imcepipeline configuration object.
    """
    failed_images = list()
    conf_input = config[c.INPUTFILES]
    file_regexp = conf_input[c.INPUTFILES_REGEXP]
    folders = conf_input[c.INPUTFILES_FOLDERS]
    conf_output = config[c.OUTPUTFOLDERS]
    folder_ome = os.path.join(conf_output[c.OUTPUTFOLDERS_BASE],
                              conf_output[c.OUTPUTFOLDERS_SUBFOLDERS][
                                  c.OUTPUTFOLDERS_SUBFOLDERS_OME])
    re_fn = re.compile(file_regexp)

    for fol in folders:
        for fn in os.listdir(fol):
            if re_fn.match(fn):
                fn_full = os.path.join(fol, fn)
                print(fn_full)
                try:
                    convertfolder2imcfolder.convert_folder2imcfolder(fn_full, out_folder=folder_ome,
                                                                    dozip=False)
                except:
                    logging.exception("Issues in file: {}".format(fn_full))

def exportacquisitionmetadata(config):
    """
    Exports the acquisition metadata into a metata csv that is readable
    by CellProfiler
    :param config: The imcepipeline configuration object.
    """
    conf_output = config[c.OUTPUTFOLDERS]
    folder_ome = os.path.join(conf_output[c.OUTPUTFOLDERS_BASE],
                              conf_output[c.OUTPUTFOLDERS_SUBFOLDERS][
                                  c.OUTPUTFOLDERS_SUBFOLDERS_OME])
    folder_cp = os.path.join(conf_output[c.OUTPUTFOLDERS_BASE],
                              conf_output[c.OUTPUTFOLDERS_SUBFOLDERS][
                                  c.OUTPUTFOLDERS_SUBFOLDERS_CP])
    exportacquisitioncsv.export_acquisition_csv(folder_ome, fol_out=folder_cp)

def generate_analysisstacks(config):
    """
    :param config: The imcepipeline configuration object.
    """
    conf_output = config[c.OUTPUTFOLDERS]
    folder_ome = os.path.join(conf_output[c.OUTPUTFOLDERS_BASE],
                              conf_output[c.OUTPUTFOLDERS_SUBFOLDERS][
                                  c.OUTPUTFOLDERS_SUBFOLDERS_OME])
    folder_analysis = os.path.join(conf_output[c.OUTPUTFOLDERS_BASE],
                              conf_output[c.OUTPUTFOLDERS_SUBFOLDERS][
                                  c.OUTPUTFOLDERS_SUBFOLDERS_ANALYSIS])

    conf_analysis = config[c.ANALYSISSTACKS]
    conf_pannel = conf_analysis[c.ANALYSISSTACKS_PANNEL]
    csv_pannel = conf_pannel[c.ANALYSISSTACKS_PANNEL_FN]
    csv_pannel_metal = conf_pannel[c.ANALYSISSTACKS_PANNEL_METALCOL]
    conf_stacks = conf_analysis[c.ANALYSISSTACKS_STACKS]

    for fol in os.listdir(folder_ome):
        sub_fol = os.path.join(folder_ome, fol)
        for img in os.listdir(sub_fol):
            if not img.endswith('.ome.tiff'):
                continue
            basename = img.rstrip('.ome.tiff')
            print(img)
            for stackconf in conf_stacks:
                col = stackconf[c.ANALYSISSTACKS_STACKS_COLUMN]
                suffix = stackconf[c.ANALYSISSTACKS_STACKS_SUFFIX]
                kwargs = stackconf.get(c.ANALYSISSTACKS_STACKS_PARAMETERS, {})
                try:
                    ometiff2analysis.ometiff_2_analysis(os.path.join(sub_fol, img), folder_analysis,
                                                    basename + suffix, pannelcsv=csv_pannel, metalcolumn=csv_pannel_metal,
                                                    usedcolumn=col, bigtiff=False,
                                                pixeltype='uint16', **kwargs)
                except:
                    logging.exception("Issues in file: {}".format(img))
