from imctools.io import ometiffparser
from imctools.io import imcacquisition
import os
import pandas


if __name__ == "__main__":
    fn = '/mnt/imls-bod/data_vito/testr231.ome.tiff'
    name = 'fullstack'
    outfolder = None
    pannel = None
    ome = ometiffparser.OmetiffParser(fn)
    imc_img = ome.get_imc_aquisition()
    metal_col = 'asdf'


    outname = '_'.join((os.path.basename(fn),name))+'.tiff'

    if outfolder is None:
        outfolder = os.path.split(fn)[0]
        outfolder = os.path.join(basefolder,'analysis')
    if not os.path.exists(outfolder):
        os.mkdir(outfolder)

    outpath= os.path.join(outfolder, outname)

    if pannel is None:
        metals = imc_img.imc_metals


    writer = imc_img.get_image_writer(outpath)
    writer.save_image(mode='imagej')


