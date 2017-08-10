
# coding: utf-8

# In[ ]:

from imctools.scripts import ometiff2analysis
from imctools.scripts import cropobjects
from imctools.scripts import croprandomsection
from imctools.scripts import resizeimage
from imctools.scripts import generatedistancetospheres
from imctools.scripts import imc2tiff
from imctools.scripts import ome2micat
from imctools.scripts import probablity2uncertainty


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
# The script can also convert mcd files directly or ZIP folders containing MCD or TXT files - please ask Vito how to adapt

# In[ ]:

# the folders with the txt/mcd files for the analysis
folders = ['/home/hartlandj/Data/METABRIC/METABRIC_txt/']

# output for OME tiffs
out_tiff_folder = '/home/jwindh/Data/VitoExample/ometiff'

# filename part that all the imc txt files should have, can be set to '' if none
common_file_part = '.txt'

# a csv indicating which columns should be used for ilastik (0, 1) in ilastik column
pannel_csv = '/home/jwindh/Data/VitoExample/configfiles/20170626_pannel_METABRICl.csv'
mass_col = None
metal_col = 'Metal Tag'
ilastik_col = 'ilastik'
# Explicitly indicates which metals should be used for the full stack
full_col = 'full'
# specify the folder to put the analysis in
analysis_folder = '/home/jwindh/Data/VitoExample/analysis'
# specify the subfolders
cp_folder = '/home/jwindh/Data/VitoExample/cpout'

uncertainty_folder = analysis_folder
micat_folder = '/home/jwindh/Data/VitoExample/micat'

# parameters for resizing the images for ilastik
suffix_full = '_full'
suffix_ilastik = '_ilastik'
suffix_ilastik_scale = '_ilastik_s2'
suffix_cropmask = 'cropmask'
suffic_segmentation = 'sphereseg'
suffix_mask = '_mask.tiff'
suffix_probablities = '_probabilities'


failed_images = list()

re_idfromname = re.compile('_l(?P<Label>[0-9]+)_')


# Specify which steps to run

# In[ ]:

do_convert_txt = False
do_stacks = True
do_ilastik = True
do_micat = True


# Generate all the folders if necessary

# In[ ]:

for fol in [out_tiff_folder, analysis_folder, cp_folder, micat_folder,uncertainty_folder]:
    if not os.path.exists(fol):
        os.makedirs(fol)


# Convert txt to ome

# In[ ]:

if do_convert_txt:
    for fol in folders:
        for fn in os.listdir(fol):
            if len([f for f in os.listdir(out_tiff_folder) if (fn.rstrip('.txt').rstrip('.mcd') in f)]) == 0:
                if common_file_part in fn: # and 'tuningtape' not in fn:
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
        if not img.endswith('.ome.tiff'):
            pass
        basename = img.rstrip('.ome.tiff')
        ometiff2analysis.ometiff_2_analysis(os.path.join(out_tiff_folder, img), analysis_folder, basename+suffix_full,
                                           pannelcsv=pannel_csv, metalcolumn=metal_col,
                                            usedcolumn=full_col)



# Generate the ilastik stacks

# In[ ]:

if do_ilastik:
    for img in os.listdir(out_tiff_folder):
        if not img.endswith('.ome.tiff'):
            pass
        basename = img.rstrip('.ome.tiff')
        ometiff2analysis.ometiff_2_analysis(os.path.join(out_tiff_folder, img), analysis_folder,
                                            basename + suffix_ilastik, pannelcsv=pannel_csv, metalcolumn=metal_col,
                                            usedcolumn=ilastik_col, addsum=True)


# -> Before the next step run the cellprofiler 'prepare_ilastik' pipeline to generate a stacks for ilastik that are scaled and have hot pixels removed
# 
# From there run the pixel classification in Ilastik either via X2GO on our server or even better on an image processing virutal machine from the ZMB.
# 
# For classification use 3 pixeltypes:
# - Nuclei
# - Cytoplasm/Membrane
# - Background
# 
# Usually it is best to label very sparsely to avoid creating a to large but redundant training data set. After initially painting few pixels, check the uncertainty frequently and only paint pixels with high uncertainty.
# 
# Once this looks nice for all the cropped sections, batch process the whole images using the code bellow. 

# In[ ]:




# ## Run the ilastik classification as a batch

# In[ ]:

fn_ilastikproject = '/home/jwindh/Data/VitoExample/pipeline/MyProject.ilp'
bin_ilastik = "/mnt/bbvolume/labcode/ilastik-1.2.0-Linux/run_ilastik.sh" 


# In[ ]:

fn_ilastik_input =os.path.join(analysis_folder,"*"+suffix_ilastik_scale+'.tiff')
glob_probabilities = os.path.join(analysis_folder,"{nickname}"+suffix_probablities+'.tiff')


# In[ ]:

get_ipython().run_cell_magic('bash', '-s "$bin_ilastik" "$fn_ilastikproject" "$glob_probabilities" "$fn_ilastik_input" ', 'echo $1\necho $2\necho $3\necho $4\nLAZYFLOW_TOTAL_RAM_MB=40000 \\\nLAZYFLOW_THREADS=16\\\n    $1 \\\n    --headless --project=$2 \\\n    --output_format=tiff \\\n    --output_filename_format=$3 \\\n    --export_dtype uint16 --pipeline_result_drange="(0.0, 1.0)" \\\n    --export_drange="(0,65535)" $4')


# ## convert probabilities to uncertainties

# In[ ]:

for fn in os.listdir(analysis_folder):
    if fn.endswith(suffix_probablities+'.tiff'):
        probablity2uncertainty.probability2uncertainty(os.path.join(analysis_folder,fn), uncertainty_folder)


# ## Generate the micat folder

# In[ ]:

if do_micat:
    if not(os.path.exists(micat_folder)):
        os.makedirs(micat_folder)
    ome2micat.omefolder2micatfolder(out_tiff_folder, micat_folder, fol_masks=cp_folder,mask_suffix=suffix_mask, dtype='uint16')

