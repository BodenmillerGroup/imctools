from ruamel.yaml import YAML

yaml = YAML()

ADDSUM = 'addsum'
INPUTFILES = 'input_files'
INPUTFILES_FOLDERS = 'folders'
INPUTFILES_REGEXP = 'file_regexp'
OUTPUTFOLDERS = 'output_folders'
OUTPUTFOLDERS_BASE  = 'base'
OUTPUTFOLDERS_SUBFOLDERS = 'subfolders'
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
{INPUTFILES}:
    {INPUTFILES_FOLDERS}: ['../example_data']
    {INPUTFILES_REGEXP}: '.'

{OUTPUTFOLDERS}:
    {OUTPUTFOLDERS_BASE}: '/home/vitoz/Data/Analysis/201811_icp_segmentation_example4'
    {OUTPUTFOLDERS_SUBFOLDERS}:
        ilastik: 'ilastik'
        ome: 'ometiff'
        cpout: 'cpout'
        uncertainty: 'uncertainty'
        histocat: 'histocat'
# This is the analysis stack configuration
{ANALYSISSTACKS}:
    {ANALYSISSTACKS_PANNEL}:
        {ANALYSISSTACKS_PANNEL_FN}: '../config/example_pannel.csv'
        {ANALYSISSTACKS_PANNEL_METALCOL}: 'Metal Tag'
    {ANALYSISSTACKS_STACKS}:
        - {ANALYSISSTACKS_STACKS_NAME}: 'full'
          {ANALYSISSTACKS_STACKS_COLUMN}: 'full'
          {ANALYSISSTACKS_STACKS_SUFFIX}: 'full'
        - {ANALYSISSTACKS_STACKS_NAME}: 'ilastik'
          {ANALYSISSTACKS_STACKS_COLUMN}: 'ilastik'
          {ANALYSISSTACKS_STACKS_SUFFIX}: 'ilastik'
          {ANALYSISSTACKS_STACKS_PARAMETERS}:
            addsum: 1
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

