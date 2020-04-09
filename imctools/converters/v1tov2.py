import glob
import logging
import os
import re
import shutil
from pathlib import Path
from typing import Sequence

from imctools.io.mcd.mcdxmlparser import McdXmlParser
from imctools.io.utils import SCHEMA_XML_SUFFIX, SESSION_JSON_SUFFIX, OME_TIFF_SUFFIX

logger = logging.getLogger(__name__)


def v1_to_v2(input_folder: str, output_folder: str, skip_csv=False):
    """Converts IMC folder from v1 to v2 format.

    Parameters
    ----------
    input_folder
        Input folder (with IMC v1 data).
    output_folder
        Output folder.
    skip_csv
        Whether to skip creation of CSV metadata files.
    """
    if not (os.path.exists(output_folder)):
        os.makedirs(output_folder)

    schema_files = glob.glob(os.path.join(input_folder, f"*{SCHEMA_XML_SUFFIX}"))
    schema_file = schema_files[0] if len(schema_files) > 0 else None

    if schema_file is None:
        raise ValueError("Input folder doesn't have a proper XML schema file.")

    with open(schema_file, "rt") as f:
        xml = f.read()

    xml_parser = McdXmlParser(xml, schema_file, process_namespaces=True)
    session = xml_parser.session
    session.save(os.path.join(output_folder, session.metaname + SESSION_JSON_SUFFIX))

    # Copy schema file
    _copy_files([schema_file], output_folder)

    # Copy slide images
    slide_files = glob.glob(os.path.join(input_folder, f"*_slide.*"))
    _copy_files(slide_files, output_folder)

    # Copy panorama images
    panorama_files = glob.glob(os.path.join(input_folder, f"*_pano.*"))
    _copy_files(panorama_files, output_folder)

    # Copy before ablation images
    before_ablation_files = glob.glob(os.path.join(input_folder, f"*_before.*"))
    _copy_files(before_ablation_files, output_folder, fix_names=True)

    # Copy after ablation images
    after_ablation_files = glob.glob(os.path.join(input_folder, f"*_after.*"))
    _copy_files(after_ablation_files, output_folder, fix_names=True)

    # Copy OME-TIFF acquisition files
    ome_tiff_files = glob.glob(os.path.join(input_folder, f"*{OME_TIFF_SUFFIX}"))
    _copy_files(ome_tiff_files, output_folder, fix_names=True)

    if not skip_csv:
        session.save_meta_csv(output_folder)


def _copy_files(filenames: Sequence[str], output_folder: str, fix_names=False):
    for fn in filenames:
        if os.path.exists(fn):
            dst = output_folder
            if fix_names:
                name = Path(fn).name
                new_name = re.sub(r"_p\d+_r\d+", "", name)
                dst = os.path.join(output_folder, new_name)
            shutil.copy2(fn, dst)


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()

    v1_to_v2(
        # "/home/anton/Documents/IMC Workshop 2019/Data/IMC_Workshop_2019_preprocessing/data/ometiff/20190919_FluidigmBrCa_SE",
        "/home/anton/Data/for Anton/new error/IMMUcan_Batch20191023_S-190701-00035",
        "/home/anton/Downloads/imc_folder_v2",
        False,
    )

    print(timeit.default_timer() - tic)
