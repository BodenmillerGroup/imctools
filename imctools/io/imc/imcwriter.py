import logging
import os
import zipfile
from pathlib import Path
from typing import Dict, Union

from imctools.io.mcd.mcdparser import McdParser
from imctools.io.txt.txtparser import TxtParser
from imctools.io.utils import OME_TIFF_SUFFIX, SCHEMA_XML_SUFFIX, SESSION_JSON_SUFFIX

logger = logging.getLogger(__name__)


IMC_ZIP_SUFFIX = "_imc.zip"


class ImcWriter:
    """Write IMC session data to IMC folder structure."""

    def __init__(
        self,
        root_output_folder: Union[str, Path],
        mcd_parser: McdParser,
        txt_acquisitions_map: Dict[int, Union[str, Path]] = None,
        parse_txt: bool = False
    ):
        """
        Initializes an ImcFolderWriter that can be used to write out an imcfolder and compress it to zip.
        """
        if isinstance(root_output_folder, str):
            root_output_folder = Path(root_output_folder)
        self.root_output_folder = root_output_folder
        self.mcd_parser = mcd_parser
        self.txt_acquisitions_map = txt_acquisitions_map
        self.parse_txt = parse_txt

    @property
    def folder_name(self):
        return self.mcd_parser.session.metaname

    def write_imc_folder(self, create_zip: bool = True, remove_folder: bool = None):
        if remove_folder is None:
            remove_folder = create_zip

        output_folder = self.root_output_folder / self.folder_name

        if not output_folder.exists():
            output_folder.mkdir(parents=True, exist_ok=True)

        session = self.mcd_parser.session

        # Save XML metadata if available
        mcd_xml = self.mcd_parser.get_mcd_xml()
        if mcd_xml is not None:
            with open(output_folder / (session.metaname + SCHEMA_XML_SUFFIX), "wt") as f:
                f.write(mcd_xml)

        # Save acquisition images in OME-TIFF format
        for acquisition in session.acquisitions.values():
            acquisition_data = self.mcd_parser.get_acquisition_data(acquisition.id)
            if self.parse_txt or not acquisition_data.is_valid:
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
                    output_folder / (acquisition.metaname + OME_TIFF_SUFFIX), xml_metadata=mcd_xml,
                )

        session.save(output_folder / (session.metaname + SESSION_JSON_SUFFIX))

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
                self.root_output_folder / (self.folder_name + IMC_ZIP_SUFFIX),
                "w",
                compression=zipfile.ZIP_DEFLATED,
                allowZip64=True,
            ) as imc_zip:
                for root, d, files in os.walk(str(output_folder)):
                    for fn in files:
                        imc_zip.write(os.path.join(root, fn), fn)
                        if remove_folder:
                            os.remove(os.path.join(root, fn))

        if remove_folder:
            os.removedirs(output_folder)


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()

    with McdParser(
        "/home/anton/Documents/IMC Workshop 2019/Data/iMC_workshop_2019/20190919_FluidigmBrCa_SE/20190919_FluidigmBrCa_SE.mcd"
    ) as parser:
        imc_writer = ImcWriter("/home/anton/Downloads/imc_from_mcd", parser)
        imc_writer.write_imc_folder()

    print(timeit.default_timer() - tic)
