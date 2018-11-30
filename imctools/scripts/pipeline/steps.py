import os
import urllib.request

from imctools.scripts import convertfolder2imcfolder
import imctools.scripts.pipeline.configuration as c

def initialize_folderstructure(config):
    """
    Initialize the folderstructure acording to the configuraiton.
    :param config: The imcepipeline configuration object.
    :returns None
	"""
    basefol = config[c.OUTPUTFOLDERS][c.OUTPUTFOLDERS_BASE]
    subfols = config[c.OUTPUTFOLDERS][c.OUTPUTFOLDERS_SUBFOLDERS]
    for fol in subfols:
        os.path.join(basefol)
        if not os.path.exists(fol):
            os.makedirs(fol)


