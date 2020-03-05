import logging
import os
import zipfile
from typing import Dict

from imctools.io.mcd.mcdparser import McdParser
from imctools.io.txt.txtparser import TxtParser
from imctools.io.utils import SCHEMA_XML_SUFFIX, OME_TIFF_SUFFIX, SESSION_JSON_SUFFIX

logger = logging.getLogger(__name__)


IMC_ZIP_SUFFIX = "_imc.zip"


class ImcWriter:
    """Write IMC session data to IMC folder structure."""

    def __init__(self, root_output_folder: str, mcd_parser: McdParser, txt_acquisitions_map: Dict[int, str] = None):
        """
        Initializes an ImcFolderWriter that can be used to write out an imcfolder and compress it to zip.
        """
        self.root_output_folder = root_output_folder
        self.mcd_parser = mcd_parser
        self.txt_acquisitions_map = txt_acquisitions_map

    @property
    def folder_name(self):
        return self.mcd_parser.session.meta_name

    def write_imc_folder(self, create_zip: bool = True, remove_folder: bool = None, skip_csv: bool = False):
        if remove_folder is None:
            remove_folder = create_zip

        output_folder = os.path.join(self.root_output_folder, self.folder_name)

        if not (os.path.exists(output_folder)):
            os.makedirs(output_folder)

        session = self.mcd_parser.session

        # Save XML metadata if available
        mcd_xml = self.mcd_parser.get_mcd_xml()
        if mcd_xml is not None:
            with open(os.path.join(output_folder, session.meta_name + SCHEMA_XML_SUFFIX), "wt") as f:
                f.write(mcd_xml)

        # Save acquisition images in OME-TIFF format
        for acquisition in session.acquisitions.values():
            acquisition_data = self.mcd_parser.get_acquisition_data(acquisition.id)
            if not acquisition_data.is_valid:
                if self.txt_acquisitions_map is not None and acquisition.id in self.txt_acquisitions_map:
                    logger.warning(f"Using TXT file for acquisition: {acquisition.id}")
                    try:
                        txt_parser = TxtParser(self.txt_acquisitions_map.get(acquisition.id), acquisition.slide_id)
                        acquisition_data = txt_parser.get_acquisition_data()
                        acquisition.origin = acquisition_data.acquisition.origin
                        acquisition.is_valid = acquisition_data.acquisition.is_valid
                    except:
                        logger.error(f"Acquisition TXT file is also corrupted")

            if acquisition_data.is_valid:
                # Calculate channels intensity range
                for ch in acquisition.channels.values():
                    img = acquisition_data.get_image_by_name(ch.name)
                    if img is not None:
                        ch.min_intensity = round(float(img.min()), 4)
                        ch.max_intensity = round(float(img.max()), 4)
                acquisition_data.save_ome_tiff(
                    os.path.join(output_folder, acquisition.meta_name + OME_TIFF_SUFFIX), xml_metadata=mcd_xml,
                )

        session.save(os.path.join(output_folder, session.meta_name + SESSION_JSON_SUFFIX))
        if not skip_csv:
            session.save_meta_csv(output_folder)

        # Save MCD file-specific artifacts like ablation images, panoramas, slide images, etc.
        for key in session.slides.keys():
            self.mcd_parser.save_slide_image(key, output_folder)

        for key in session.panoramas.keys():
            self.mcd_parser.save_panorama_image(key, output_folder)

        for key in session.acquisitions.keys():
            self.mcd_parser.save_before_ablation_image(key, output_folder)
            self.mcd_parser.save_after_ablation_image(key, output_folder)

        if create_zip:
            with zipfile.ZipFile(
                os.path.join(self.root_output_folder, self.folder_name + IMC_ZIP_SUFFIX),
                "w",
                compression=zipfile.ZIP_DEFLATED,
                allowZip64=True,
            ) as imc_zip:
                for root, d, files in os.walk(output_folder):
                    for fn in files:
                        imc_zip.write(os.path.join(root, fn), fn)
                        if remove_folder:
                            os.remove(os.path.join(root, fn))

        if remove_folder:
            os.removedirs(output_folder)


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()

    with McdParser("/home/anton/Downloads/test/IMMUcan_Batch20191023_10032401-HN-VAR-TIS-01-IMC-01_AC2.mcd") as parser:
        imc_writer = ImcWriter("/home/anton/Downloads/imc_from_mcd", parser)
        imc_writer.write_imc_folder()

    print(timeit.default_timer() - tic)
