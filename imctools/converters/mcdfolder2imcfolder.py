import os
import glob
import zipfile
import logging
from tempfile import TemporaryDirectory

from imctools.io.imc.imcwriter import ImcWriter
from imctools.io.mcd.mcdparser import McdParser
from imctools.io.txt.txtparser import TxtParser, TXT_FILE_EXTENSION

logger = logging.getLogger(__name__)

MCD_FILENDING = ".mcd"
ZIP_FILENDING = ".zip"
SCHEMA_FILENDING = ".schema"


def mcd_folder_to_imc_folder(input: str, output_folder: str, create_zip: bool = False):
    """
    Converts folder containing raw acquisition data (mcd and txt files) to IMC folder containing standardized files.
    """
    tmpdir = None
    if input.endswith(ZIP_FILENDING):
        tmpdir = TemporaryDirectory()
        with zipfile.ZipFile(input, allowZip64=True) as zip:
            zip.extractall(tmpdir.name)
        input_folder = tmpdir.name
    else:
        input_folder = input

    try:
        mcd_files = glob.glob(os.path.join(input_folder, f"*{MCD_FILENDING}"))
        assert len(mcd_files) == 1
        schema_files = glob.glob(os.path.join(input_folder, f"*{SCHEMA_FILENDING}"))
        schema_file = schema_files[0] if len(schema_files) > 0 else None
        try:
            mcd_parser = McdParser(mcd_files[0], xml_metadata_filepath=schema_file) # McdParser(mcd_files[0])
        except:
            if schema_file is not None:
                logging.error("MCD file is corrupted, trying to rescue with schema file")
                mcd_parser = McdParser(mcd_files[0], xml_metadata_filepath=schema_file)
            else:
                raise

        txt_files = glob.glob(os.path.join(input_folder, f"*[0-9]{TXT_FILE_EXTENSION}"))
        txt_acquisitions_map = {TxtParser.extract_acquisition_id(f): f for f in txt_files}
        # txt_only_ac_ids = set(txt_ac_ids.keys()).difference(set(mcd_parser.session.acquisition_indices))
        # for txt_ac_id in txt_only_ac_ids:
        #     logger.warning("Using TXT file for acquisition: " + txt_ac_id)
        #     try:
        #         acquisition_data = TxtParser(txt_ac_ids[txt_ac_id]).get_acquisition_data()
        #     except:
        #         logger.error("TXT file is also corrupted.")

        imc_writer = ImcWriter(output_folder, mcd_parser, txt_acquisitions_map)
        imc_writer.write_imc_folder(create_zip=create_zip)
    finally:
        mcd_parser.close()
        if tmpdir is not None:
            tmpdir.cleanup()


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()

    mcd_folder_to_imc_folder(
        "/home/anton/Data/20190529_TH_Tonsil_CXCR_CCR_panel2",
        "/home/anton/Downloads/imc_folder",
    )

    print(timeit.default_timer() - tic)
