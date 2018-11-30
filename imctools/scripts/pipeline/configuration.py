from ruamel.yaml import YAML

yaml = YAML()

INPUTFILES = 'input_files'
INPUTFILES_FOLDERS = 'folders'
INPUTFILES_REGEXP = 'file_regexp'
OUTPUTFOLDERS = 'output_folders'
OUTPUTFOLDERS_BASE  = 'base'
OUTPUTFOLDERS_SUBFOLDERS = 'subfolders'
OUTPUTFOLDERS_SUBFOLDERS_OME = 'ome'
OUTPUTFOLDERS_SUBFOLDERS_CP = 'cpout'
OUTPUTFOLDERS_SUBFOLDERS_ANALYSIS = 'analysis'
ANALYSISSTACKS = 'analysis_stack_generation'
ANALYSISSTACKS_PANNEL = 'pannel'
ANALYSISSTACKS_PANNEL_FN = 'csv_filename'
ANALYSISSTACKS_PANNEL_METALCOL = 'metal_column'
ANALYSISSTACKS_STACKS = 'stacks'
ANALYSISSTACKS_STACKS_NAME = 'stack_name'
ANALYSISSTACKS_STACKS_COLUMN = 'csv_column'
ANALYSISSTACKS_STACKS_SUFFIX = 'suffix'
ANALYSISSTACKS_STACKS_PARAMETERS = 'additional_parameters'

conf_str = f"""
# This section specifies the input files.
{INPUTFILES}:
    # This defines a list of folders  where to look for input files which must be zip files
    # containing each 1 .mcd file together with (optionally)  all the .txt files of this
    # acquisition session.
    {INPUTFILES_FOLDERS}: ['../example_data']
    # This regular expression can be used to further select .zip files for processing
    {INPUTFILES_REGEXP}: '.zip'

# This section defines the output folders
{OUTPUTFOLDERS}:
    # This indicates the base folder for all the output subfolders:
    {OUTPUTFOLDERS_BASE}: '/home/vitoz/Data/Analysis/201811_icp_segmentation_example4'
    {OUTPUTFOLDERS_SUBFOLDERS}:
        # The ome subfolder contains all the acquisitions as ometiffs together with the
        # metadata in .csv format.
        {OUTPUTFOLDERS_SUBFOLDERS_OME}: 'ometiff'
        # The cpout subfolder will contain the final cellprofiler output.
        {OUTPUTFOLDERS_SUBFOLDERS_CP}: 'cpout'
        # The analysis subfolder will contain all the .zip files that are used for analysis.
        {OUTPUTFOLDERS_SUBFOLDERS_ANALYSIS}: 'analysis'
        # The ilastik folder will contain all the .hd5 files used for Ilastik Pixel classification.
        ilastik: 'ilastik'
        # The uncertainty folder can contain the uncertainties that can be generated from the
        # probabiprobabilities from the Ilastik pixel classification.
        uncertainty: 'uncertainty'
        # The Histocat folder will contain the images in the HistoCat folder structure.
        histocat: 'histocat'

# This configuration saves different substacks of the acquired images in a format compatible for
# analanalysis with CellProfiler and Ilastik.
{ANALYSISSTACKS}:
    # The pannel is a CSV file with a column representing the metal tag and a column containing
    # boolean (0/1) values which channels to select for the different stacks.
    {ANALYSISSTACKS_PANNEL}:
        # The filename of the pannel .csv file
        {ANALYSISSTACKS_PANNEL_FN}: '../config/example_pannel.csv'
        # The name of the column containing the metal tag
        {ANALYSISSTACKS_PANNEL_METALCOL}: 'Metal Tag'
    # An arbitrary number of stacks can be defined. Classically a 'full' stack is defined,
    # containing all the channels(=metals) that should be measured using CellProfiler as well as
    # an 'ilastik' stack, containing only a subset of channels that contain information for the
    # pixelpixel classification used for segmentation.
    {ANALYSISSTACKS_STACKS}:
        # The stack name indicated the name of the stack to be generated
        - {ANALYSISSTACKS_STACKS_NAME}: 'full'
          # The stack column is the column that contains the boolean selection for the channels to
          # be used for this stack
          {ANALYSISSTACKS_STACKS_COLUMN}: 'full'
          # The suffix is added to the filename before the file ending and is used to identify the
          # stack in the later analysis.
          {ANALYSISSTACKS_STACKS_SUFFIX}: '_full'

        - {ANALYSISSTACKS_STACKS_NAME}: 'ilastik'
          {ANALYSISSTACKS_STACKS_COLUMN}: 'ilastik'
          {ANALYSISSTACKS_STACKS_SUFFIX}: '_ilastik'
          # With aditional stack parameters, keyword arguments used by the ometiff_2_analysis script
          {ANALYSISSTACKS_STACKS_PARAMETERS}:
            # A commonly used one parameter to set is 'addsum', which will add the sum of all channels of the stack as
            # first channel of the stack, which is convenient for forground/background
            # discrimination in pixel classification.
            addsum: True
"""

def load_config(filename):
    """
    Loads the configuration file.
    :param filename: filepath to the configuration file
    :returns A configuration file dictionary
    """
    with open(filename, 'r') as f:
        conf = yaml.load(f)
    return conf

def save_config(config, filename):
    """
    Saves the configuration file
    :param config: the configuration script
    :param filename: the path to the configuration file
    """
    with open(filename, 'w') as f:
        yaml.dump(config, f)

def get_example_config():
    return yaml.load(conf_str)

