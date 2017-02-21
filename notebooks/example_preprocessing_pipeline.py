
# coding: utf-8

# In[ ]:

from imctools.scripts import ometiff2analysis
from imctools.scripts import cropobjects
from imctools.scripts import croprandomsection
from imctools.scripts import resizeimage
from imctools.scripts import generatedistancetospheres
from imctools.scripts import imc2tiff
from imctools.scripts import ome2micat



# In[ ]:




# In[ ]:

import os
import re


# 
# # This script must be adapted to use
# Currently it will convert txt in subfolders of the folder base_folder into OME.tiffs
#  and then create tiff stacks for analysis and ilastik based on the pannel_csv
#  run it like this
#  this will create crops for ilastik
#  load the ilatik_random folder in ilastik and do the classifictation
#  check the uncertainties
# 

# In[ ]:

# the folders with the txt/mcd files for the analysis
folders = ['/path/to/txt/file/folder']

# output for OME tiffs
out_tiff_folder = 'path/to/output/folder'

# filename part that all the imc txt files should have, can be set to '' if none
common_file_part = 'txt'

# a csv indicating which columns should be used for ilastik (0, 1) in ilastik column
pannel_csv = '../example/panel.csv'
mass_col = None
metal_col = 'Metal'
ilastik_col = 'ilastik'
# specify the folder to put the analysis in
analysis_folder = '../testout/analysis_stacks'
# specify the subfolders
ilastik_randomfolder = '../testout/ilastik_random'
cp_folder = '../testout/cpoutput/'
micat_folder = '../testout/micat/'

pannel_csv = '/home/daniels/Data/Her2_TMA/Her2_TMA_final_for_stack_generation.csv'
mass_col = None
metal_col = 'Metal'
ilastik_col = 'ilastik'

# parameters for resizing the images for ilastik
resize_scale = 2
suffix_full = '_full'
suffix_ilastik = '_ilastik'
suffix_ilastik_scale = '_ilastik'+str(resize_scale)
suffix_cropmask = 'cropmask'
suffic_segmentation = 'sphereseg'
suffix_mask = '_mask.tiff'
suffix_probablities = '_probabilities'

# size of the random crops
random_cropsize = 250
# how many random crops should be made
n_random_crops = 1


failed_images = list()

re_idfromname = re.compile('_l(?P<Label>[0-9]+)_')


# In[ ]:

suffix_ilastik_scale


# Specify which steps to run

# In[ ]:

do_convert_txt = True
do_stacks = True
do_ilastik = True
do_ilastik_crop = True
do_micat = True


# Generate all the folders if necessary

# In[ ]:

for fol in [out_tiff_folder, analysis_folder, ilastik_randomfolder, cp_folder, micat_folder]:
    if not os.path.exists(fol):
        os.makedirs(fol)


# Convert txt to ome

# In[ ]:

if do_convert_txt:
    for fol in folders:
        for fn in os.listdir(fol):
            if len([f for f in os.listdir(out_tiff_folder) if (fn.rstrip('.txt') in f)]) == 0:
                if common_file_part in fn:
                    print(fn)
                    txtname = os.path.join(fol, fn)
                    try:
                        imc2tiff.save_imc_to_tiff(txtname,tifftype='ome', outpath=out_tiff_folder)

                    except:
                        failed_images.append(txtname)
                        print(txtname)


# Generate the analysis stacks

# In[ ]:

if do_stacks:
    for img in os.listdir(out_tiff_folder):
        basename = img.rstrip('.ome.tiff')
        ometiff2analysis.ometiff_2_analysis(os.path.join(out_tiff_folder, img), analysis_folder, basename+suffix_full)



# Generate the ilastik stacks

# In[ ]:

if do_ilastik:
    for img in os.listdir(out_tiff_folder):
        basename = img.rstrip('.ome.tiff')
        ometiff2analysis.ometiff_2_analysis(os.path.join(out_tiff_folder, img), analysis_folder,
                                            basename + suffix_ilastik, pannelcsv=pannel_csv, metalcolumn=metal_col,
                                            usedcolumn=ilastik_col)

        # resize the ilastik image
        fn = os.path.join(analysis_folder, basename + suffix_ilastik + '.tiff')
        resizeimage.resize_image(fn,
                                 outfolder=analysis_folder, basename=basename + suffix_ilastik_scale,
                                 scalefactor=resize_scale)

        os.remove(fn)



# Generate the ilastik random crops

# In[ ]:

if do_ilastik_crop:
    for fn in os.listdir(analysis_folder):
        if (fn.endswith(suffix_ilastik_scale + '.tiff')):
            fn_base = fn.rstrip('.tiff').rstrip('.tif')
            fn = os.path.join(analysis_folder, fn)
            for i in range(n_random_crops):
                croprandomsection.crop_random_section(fn, outfolder=ilastik_randomfolder, basename=fn_base,
                                                  size=random_cropsize)

print(failed_images)


# -> Before the next step run ilastik, then cellprofiler to generate the masks

# ## Run the ilastik classification as a batch

# In[ ]:

fn_ilastikproject = '/path/to/ilastik_project.ilp'
bin_ilastik = "/mnt/bbvolume/labcode/ilastik-1.2.0-Linux/run_ilastik.sh" 


# In[ ]:

glob_probabilities =os.path.join(analysis_folder,"*"+suffix_ilastik_scale+'.tiff')
fn_ilastik_out = os.path.join(analysis_folder,"{nickname}"+suffix_probablities+'.tiff')


# In[ ]:

get_ipython().run_cell_magic('bash', '-s "$bin_ilastik" "$fn_ilastikproject" "$glob_probabilities" "$fn_ilastik_out" ', 'echo $1\necho $2\necho $3\necho $4\nLAZYFLOW_TOTAL_RAM_MB=40000 \\\nLAZYFLOW_THREADS=16\\\n    $1 \\\n    --headless --project=$2 \\\n    --output_format=tiff \\\n    --output_filename_format=$3 \\\n    --export_dtype uint16 --pipeline_result_drange="(0.0, 1.0)" \\\n    --export_drange="(0,65535)" $4')


# ## Generate the micat folder

# In[ ]:

if do_micat:
    if not(os.path.exists(micat_folder)):
        os.makedirs(micat_folder)
    ome2micat.omefolder2micatfolder(out_tiff_folder, micat_folder, fol_masks=cp_folder,mask_suffix=suffix_mask, dtype='uint16')

