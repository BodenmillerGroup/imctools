import logging
import mmap
import os
from typing import BinaryIO

import numpy as np

import imctools.io.mcd.constants as const
from imctools.data import Acquisition
from imctools.io.imc.imcwriter import ImcWriter
from imctools.io.mcd.mcdxmlparser import McdXmlParser
from imctools.io.parserbase import ParserBase
from imctools.io.utils import reshape_long_2_cyx

logger = logging.getLogger(__name__)


class McdParser(ParserBase):
    """Raw MCD file parser.

    The McdParser object should be closed using the close method
    """
    def __init__(self, filepath: str, file_handle: BinaryIO = None, xml_metadata_filepath: str = None):
        ParserBase.__init__(self)
        if file_handle is None:
            self._fh = open(filepath, mode="rb")
        else:
            self._fh = file_handle

        if xml_metadata_filepath is None:
            self._meta_fh = self._fh
        else:
            self._meta_fh = open(xml_metadata_filepath, mode="rb")

        footer = self._get_footer()
        public_xml_start = footer.find("<MCDPublic")
        xml = footer[:public_xml_start]
        self._xml_parser = McdXmlParser(xml, self._fh.name)

    @property
    def origin(self):
        return self._xml_parser.origin

    @property
    def session(self):
        return self._xml_parser.session

    @property
    def filename(self):
        """Return the name of the open file

        """
        return self._fh.name

    @property
    def xml_metadata(self):
        return self._xml_parser.xml_metadata

    def _get_acquisition_raw_data(self, acquisition: Acquisition):
        """Gets non-reshaped image data from the acquisition

        Parameters
        ----------
        acquisition
            Acquisition
        """
        start_offset = int(acquisition.metadata.get(const.DATA_START_OFFSET))
        end_offset = int(acquisition.metadata.get(const.DATA_END_OFFSET))
        # Taking into account 3 dropped channels X, Y, Z!
        total_n_channels = len(acquisition.channels) + 3
        data_size = end_offset - start_offset + 1
        data_nrows = int(data_size / (total_n_channels * int(acquisition.metadata.get(const.VALUE_BYTES))))
        if data_nrows == 0:
            logger.error(f"Acquisition {acquisition.meta_name} is emtpy")
            return None
            # raise AcquisitionError(f"Acquisition {acquisition.id} is emtpy!")

        data = np.memmap(
            self._fh, dtype=np.float32, mode="r", offset=start_offset, shape=(data_nrows, total_n_channels)
        )
        return data

    def _inject_imc_datafile(self, filename: str):
        """
        This function is used in cases where the MCD file is corrupted (missing MCD schema)
        but there is a MCD schema file available. In this case the .schema file can
        be loaded with the mcdparser and then the corrupted mcd-data file loaded
        using this function. This will replace the mcd file data in the backend (containing only
        the schema data) with the real mcd file (not containing the mcd xml).
        """
        self.close()
        self._fh = open(filename, mode="rb")

    def _get_footer(self, start_str: str = "<MCDSchema", encoding: str = "utf-16-le"):
        with mmap.mmap(self._meta_fh.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            # MCD format documentation recommends searching from end for "<MCDSchema"
            offset = mm.rfind(start_str.encode(encoding))
            if offset == -1:
                raise ValueError(f"'{self.filename}' does not contain MCDSchema XML footer (try different encoding?).")
            mm.seek(offset)
            footer: str = mm.read().decode(encoding)
            return footer

    def get_acquisition_image_data(self, acquisition: Acquisition):
        """Returns an ImcAcquisition object corresponding to the ac_id"""
        data = self._get_acquisition_raw_data(acquisition)
        if data is not None:
            image_data = reshape_long_2_cyx(data, is_sorted=True)
            # Drop first three channels X, Y, Z
            image_data = image_data[3:]
            acquisition.image_data = image_data
        return acquisition

    def save_panorama_image(self, panorama_id: int, out_folder: str, fn_out=None):
        """Save panorama image of the acquisition"""
        panorama_postfix = "pano"
        image_offset_fix = 161
        p = self.session.panoramas.get(panorama_id)
        img_start = int(p.metadata.get(const.IMAGE_START_OFFSET, 0)) + image_offset_fix
        img_end = int(p.metadata.get(const.IMAGE_END_OFFSET, 0)) + image_offset_fix

        if img_start - img_end == 0:
            return 0

        file_end = p.metadata.get(const.IMAGE_FORMAT, ".png").lower()

        if fn_out is None:
            fn_out = p.meta_name

        if not (fn_out.endswith(file_end)):
            fn_out += "_" + panorama_postfix + "." + file_end

        buf = self._get_buffer(img_start, img_end)
        with open(os.path.join(out_folder, fn_out), "wb") as f:
            f.write(buf)

    def save_slide_image(self, slide_id: int, out_folder: str, fn_out=None):
        image_offset_fix = 161
        slide_postfix = "slide"
        default_format = ".png"

        s = self.session.slides.get(slide_id)
        img_start = int(s.metadata.get(const.IMAGE_START_OFFSET, 0)) + image_offset_fix
        img_end = int(s.metadata.get(const.IMAGE_END_OFFSET, 0)) + image_offset_fix
        slide_format = s.metadata.get(const.IMAGE_FILE, default_format)
        if slide_format in [None, "", '""', "''"]:
            slide_format = default_format

        slide_format = os.path.splitext(slide_format.lower())
        if slide_format[1] == "":
            slide_format = slide_format[0]
        else:
            slide_format = slide_format[1]

        if img_start - img_end == 0:
            return 0

        if fn_out is None:
            fn_out = s.meta_name
        if not (fn_out.endswith(slide_format)):
            fn_out += "_" + slide_postfix + slide_format

        buf = self._get_buffer(img_start, img_end)
        with open(os.path.join(out_folder, fn_out), "wb") as f:
            f.write(buf)

    def save_before_ablation_image(self, acquisition_id: int, out_folder: str, fn_out=None):
        self._save_ablation_image(
            acquisition_id,
            out_folder,
            "before",
            const.BEFORE_ABLATION_IMAGE_START_OFFSET,
            const.BEFORE_ABLATION_IMAGE_END_OFFSET,
            fn_out,
        )

    def save_after_ablation_image(self, acquisition_id: int, out_folder: str, fn_out=None):
        self._save_ablation_image(
            acquisition_id,
            out_folder,
            "after",
            const.AFTER_ABLATION_IMAGE_START_OFFSET,
            const.AFTER_ABLATION_IMAGE_END_OFFSET,
            fn_out,
        )

    def _save_ablation_image(
        self, acquisition_id: int, output_folder: str, ac_postfix: str, start_offset: str, end_offset: str, fn_out=None
    ):
        image_offset_fix = 161
        image_format = ".png"
        a = self.session.acquisitions.get(acquisition_id)
        img_start = int(a.metadata.get(start_offset, 0)) + image_offset_fix
        img_end = int(a.metadata.get(end_offset, 0)) + image_offset_fix
        if img_end - img_start == 0:
            return 0

        if fn_out is None:
            fn_out = a.meta_name
        buf = self._get_buffer(img_start, img_end)
        if not (fn_out.endswith(image_format)):
            fn_out += "_" + ac_postfix + image_format
        with open(os.path.join(output_folder, fn_out), "wb") as f:
            f.write(buf)

    def save_xml_metadata(self, output_folder: str):
        """Save original raw XML metadata from .mcd file into a separate .xml file

        Parameters
        ----------
        output_folder
            Output file directory. Filename will be generated automatically using IMC session name.
        """
        filename = self.session.meta_name + ".xml"
        with open(os.path.join(output_folder, filename), "wt") as f:
            f.write(self.xml_metadata)

    def save_artifacts(self, output_folder: str):
        """Save MCD file-specific artifacts like ablation images, panoramas, slide images, etc."""
        for key in self.session.slides.keys():
            self.save_slide_image(key, output_folder)

        for key in self.session.panoramas.keys():
            self.save_panorama_image(key, output_folder)

        for key in self.session.acquisitions.keys():
            self.save_before_ablation_image(key, output_folder)
            self.save_after_ablation_image(key, output_folder)

    def save_imc_folder(self, output_folder: str):
        for acquisition in self.session.acquisitions.values():
            self.get_acquisition_image_data(acquisition)
        imc_writer = ImcWriter(self)
        imc_writer.save_imc_folder(output_folder)

    def _get_buffer(self, start: int, stop: int):
        self._fh.seek(start)
        buf = self._fh.read(stop - start)
        return buf

    def close(self):
        """Close file handles"""
        self._fh.close()
        try:
            self._meta_fh.close()
        except:
            pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()

    filename = "/home/anton/Downloads/test/IMMUcan_Batch20191023_10032401-HN-VAR-TIS-01-IMC-01_AC2.mcd"
    with McdParser(filename) as parser:
        parser.save_imc_folder("/home/anton/Downloads/imc_from_mcd")

    print(timeit.default_timer() - tic)
