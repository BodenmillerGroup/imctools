import glob
import logging
import os
import re
import shutil
from pathlib import Path
from typing import Sequence

from imctools.data import Session
from imctools.io.mcd.mcdxmlparser import McdXmlParser
from imctools.io.ometiff.ometiffparser import OmeTiffParser
from imctools.io.utils import SCHEMA_XML_SUFFIX, SESSION_JSON_SUFFIX, OME_TIFF_SUFFIX

logger = logging.getLogger(__name__)


def v1_to_v2(input_folder: str, output_folder: str):
    """Converts IMC folder from v1 to v2 format.

    Parameters
    ----------
    input_folder
        Input folder (with IMC v1 data).
    output_folder
        Output folder.
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
    session = _calculate_min_max_intensities(ome_tiff_files, session)
    session.save(os.path.join(output_folder, session.metaname + SESSION_JSON_SUFFIX))
    _copy_files(ome_tiff_files, output_folder, fix_names=True)


def _calculate_min_max_intensities(filenames: Sequence[str], session: Session):
    """Calculate min and max intensity of each channel."""
    for fn in filenames:
        with OmeTiffParser(fn) as parser:
            ac_data = parser.get_acquisition_data()
            acquisition = session.acquisitions.get(ac_data.acquisition.id)
            if acquisition:
                for channel in acquisition.channels.values():
                    img = ac_data.get_image_by_name(channel.name)
                    session.channels[channel.id].min_intensity = round(float(img.min()), 4)
                    session.channels[channel.id].max_intensity = round(float(img.max()), 4)
    return session


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
    )

    print(timeit.default_timer() - tic)
