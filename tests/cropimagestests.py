from imctools.scripts import cropobjects
import os
fn_label = '/home/vitoz/temp/20150330_IS2335_5um_3_site1_ac2_200hz_2200x2200/analysis/20150330_IS2335_5um_3_site1_ac2_200hz_2200x2200_ilastik_labels.tif'
fn_stack = '/home/vitoz/temp/20150330_IS2335_5um_3_site1_ac2_200hz_2200x2200/analysis/20150330_IS2335_5um_3_site1_ac2_200hz_2200x2200_ilastik.tiff'
outfolder = '/home/vitoz/temp/20150330_IS2335_5um_3_site1_ac2_200hz_2200x2200/analysis/crops'
basename = os.path.split(fn_stack)[1].strip('.tif').strip('.tiff')

scale = 2
extend = 20

cropobjects.crop_objects(fn_stack, fn_label, outfolder, basename, extend)

basename = os.path.split(fn_label)[1].strip('.tif').strip('.tiff')
scale=1
cropobjects.crop_objects(fn_label, fn_label, outfolder, basename, extend)