from imctools.scripts import resizeimage
import os
fn_stack = '/home/vitoz/temp/20150330_IS2335_5um_3_site1_ac2_200hz_2200x2200/analysis/crops'
outfolder = '/home/vitoz/temp/20150330_IS2335_5um_3_site1_ac2_200hz_2200x2200/analysis/crops2x'
basename = os.path.split(fn_stack)[1].strip('.tif').strip('.tiff')

factor = 2

fns = os.listdir(fn_stack)

for fn in fns:
    if '.tif' in fn:
        resizeimage.resize_image(os.path.join(fn_stack,fn), outfolder, fn.strip('.tiff').strip('.tif'), factor)
