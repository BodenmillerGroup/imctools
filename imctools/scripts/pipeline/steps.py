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


class ImcPipeline(object):
    def __init__(self, config=None):
        self.config = None

    def config_load(self, fn_conf):
        self.config = c.load_config(fn_conf)

    def config_save(self, fn_conf):
        c.save_config(fn_conf)

    @property
    def config_input(self):
        return self.config[c.INPUTFILES]

    @property
    def config_output(self):
        return self.config[c.OUTPUTFOLDERS]

    @property
    def config_analysis(self):
        return self.config[c.ANALYSISSTACKS]

    @property
    def basefolder(self):
        return self.config_output[c.OUTPUTFOLDERS_BASE]

    @basefolder.setter
    def basefolder(self, fol):
        self.config_output[c.OUTPUTFOLDERS_BASE] = fol

    def initialize_folderstructure(self):
        """
        Initialize the folderstructure acording to the configuraiton.
        :param config: The imcepipeline configuration object.
        :returns None
        """
        config = self.config
        basefol = self.basefolder
        subfols_dict = self.config_output[c.OUTPUTFOLDERS_SUBFOLDERS]
        subfols = subfols_dict.values()
        for fol in subfols:
            fol = os.path.join(basefol, fol)
            if not os.path.exists(fol):
                os.makedirs(fol)

    def convert_rawzip_to_ome(self):
        """
        Converts the rawdata (zipped acquisitions with 1 mcd and all .txt
        files) to folders containing the images as .ome tiffs.
        :param config: The imcepipeline configuration object.
        """
        config = self.config
        conf_input = self.config_input
        file_regexp = conf_input[c.INPUTFILES_REGEXP]
        folders = conf_input[c.INPUTFILES_FOLDERS]
        conf_output = config[c.OUTPUTFOLDERS]
        folder_ome = os.path.join(self.basefolder,
                                  conf_output[c.OUTPUTFOLDERS_SUBFOLDERS][
                                    c.OUTPUTFOLDERS_SUBFOLDERS_OME])
        re_fn = re.compile(file_regexp)

        for fol in folders:
            for fn in os.listdir(fol):
                if re_fn.match(fn):
                    fn_full = os.path.join(fol, fn)
                    print(fn_full)
                    try:
                        convertfolder2imcfolder.convert_folder2imcfolder(
                            fn_full,
                            out_folder=folder_ome,
                            dozip=False)
                    except:
                        logging.exception("Issues in file: {}".format(fn_full))

    def exportacquisitionmetadata(self):
        """
        Exports the acquisition metadata into a metata csv that is readable
        by CellProfiler
        :param config: The imcepipeline configuration object.
        """
        config = self.config
        conf_output = self.config_output
        conf_subfols = conf_output[c.OUTPUTFOLDERS_SUBFOLDERS]
        fol_base = self.basefolder
        folder_ome, folder_cp = (os.path.join(fol_base, conf_subfols[sf])
                                 for sf in (
                                       c.OUTPUTFOLDERS_SUBFOLDERS_OME,
                                       c.OUTPUTFOLDERS_SUBFOLDERS_CP))
        exportacquisitioncsv.export_acquisition_csv(folder_ome,
                                                    fol_out=folder_cp)

    def generate_analysisstacks(self):
        """
        :param config: The imcepipeline configuration object.
        """
        config = self.config
        conf_output = self.config_output
        conf_subfols = conf_output[c.OUTPUTFOLDERS_SUBFOLDERS]
        fol_base = self.basefolder
        folder_ome, folder_analysis = (os.path.join(fol_base, conf_subfols[sf])
                                       for sf in (
                                          c.OUTPUTFOLDERS_SUBFOLDERS_OME,
                                          c.OUTPUTFOLDERS_SUBFOLDERS_ANALYSIS))

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
                for stackconf in conf_stacks.values():
                    col = stackconf[c.ANALYSISSTACKS_STACKS_COLUMN]
                    suffix = stackconf[c.ANALYSISSTACKS_STACKS_SUFFIX]
                    set_kwargs = stackconf.get(c.ANALYSISSTACKS_STACKS_PARAMETERS,
                                           {})
                    default_kwargs = {
                        'outfolder': out_folder_analysis,
                        'basename': basename + suffix,
                        'pannelcsv':csv_pannel,
                        'metalcolumn': csv_pannel_metal,
                        'usedcolumn': col,
                        'bigtiff': False,
                        'pixeltype': 'uint16'}
                    kwargs = default_kwargs.update(set_kwargs)
                    try:
                        ometiff2analysis.ometiff_2_analysis(
                            os.path.join(sub_fol, img),
                            **kwargs)
                    except:
                        logging.exception("Issues in file: {}".format(img))
