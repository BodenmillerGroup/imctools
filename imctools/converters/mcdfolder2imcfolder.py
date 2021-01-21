import glob
import logging
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Union

from imctools.io.imc.imcwriter import ImcWriter
from imctools.io.mcd.mcdparser import McdParser
from imctools.io.txt.txtparser import TXT_FILE_EXTENSION, TxtParser
from imctools.io.utils import MCD_FILENDING, SCHEMA_FILENDING, ZIP_FILENDING

logger = logging.getLogger(__name__)


def mcdfolder_to_imcfolder(input: Union[str, Path], output_folder: Union[str, Path], create_zip: bool = False, parse_txt: bool = False):
    """Converts folder (or zipped folder) containing raw acquisition data (mcd and txt files) to IMC folder containing standardized files.

    Parameters
    ----------
    input
        Input folder / .zip file with  raw .mcd/.txt acquisition data files.
    output_folder
        Path to the output folder.
    create_zip
        Whether to create an output as .zip file.
    parse_txt
        Always use TXT files if present to get acquisition image data.
    """
    if isinstance(input, str):
        input = Path(input)
    tmpdir = None
    if input.is_file() and input.suffix == ZIP_FILENDING:
        tmpdir = TemporaryDirectory()
        with zipfile.ZipFile(input, allowZip64=True) as zip:
            zip.extractall(tmpdir.name)
        input_folder = Path(tmpdir.name)
    else:
        input_folder = input

    mcd_parser = None
    try:
        mcd_files = list(input_folder.rglob(f"*{MCD_FILENDING}"))
        mcd_files = [f for f in mcd_files if not f.name.startswith(".")]
        assert len(mcd_files) == 1
        schema_files = glob.glob(str(input_folder / f"*{SCHEMA_FILENDING}"))
        schema_file = schema_files[0] if len(schema_files) > 0 else None
        try:
            mcd_parser = McdParser(mcd_files[0])
        except:
            if schema_file is not None:
                logging.error("MCD file is corrupted, trying to rescue with schema file")
                mcd_parser = McdParser(mcd_files[0], xml_metadata_filepath=schema_file)
            else:
                raise

        txt_files = glob.glob(str(input_folder / f"*[0-9]{TXT_FILE_EXTENSION}"))
        txt_acquisitions_map = {TxtParser.extract_acquisition_id(f): f for f in txt_files}

        imc_writer = ImcWriter(output_folder, mcd_parser, txt_acquisitions_map, parse_txt)
        imc_writer.write_imc_folder(create_zip=create_zip)
    finally:
        if mcd_parser is not None:
            mcd_parser.close()
        if tmpdir is not None:
            tmpdir.cleanup()


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()

    mcdfolder_to_imcfolder(
        # Path("/home/anton/Downloads/20170905_Fluidigmworkshopfinal_SEAJa.zip"),
        # "/home/anton/Downloads/20170905_Fluidigmworkshopfinal_SEAJa",
        "/home/anton/Data/forAnton_MCD/6505_Lympho",
        # "/home/anton/Documents/merrick/IMC/20200904_MS_XRF_epithelial_panel_4_titration.zip",
        # "/home/anton/Documents/IMC Workshop 2019/Data/iMC_workshop_2019/20190919_FluidigmBrCa_SE",
        # "/home/anton/Downloads/test",
        # "/home/anton/Data/ForAnton/20200123_IMMUcan_reproducibility_day1_sl1_cp_panel_1_1.06.zip",
        Path("/home/anton/Downloads/imc_folder_v2"),
        create_zip=False,
        parse_txt=True
    )

    print(timeit.default_timer() - tic)
