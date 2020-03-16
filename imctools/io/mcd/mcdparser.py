import logging
from pathlib import Path

import mmap
import os
from typing import BinaryIO, Optional, Union

import numpy as np

import imctools.io.mcd.constants as const
from imctools.data import Acquisition, AblationImageType
from imctools.data.acquisitiondata import AcquisitionData
from imctools.io.mcd.mcdxmlparser import McdXmlParser
from imctools.io.utils import reshape_long_2_cyx

logger = logging.getLogger(__name__)


class McdParser:
    """Raw MCD file parser.

    The McdParser object should be closed using the close method
    """

    def __init__(self, filepath: Union[str, Path], file_handle: BinaryIO = None, xml_metadata_filepath: str = None):
        if file_handle is None:
            self._fh = open(filepath, mode="rb")
        else:
            self._fh = file_handle

        if xml_metadata_filepath is None:
            self._meta_fh = self._fh
        else:
            self._meta_fh = open(xml_metadata_filepath, mode="rb")

        encoding = "utf-8" if xml_metadata_filepath is not None else "utf-16-le"
        mcd_xml = self._get_mcd_xml(encoding=encoding)
        self._xml_parser = McdXmlParser(mcd_xml, self._fh.name)

    @property
    def origin(self):
        return self._xml_parser.origin

    @property
    def session(self):
        return self._xml_parser.session

    def get_mcd_xml(self):
        """Original (raw) metadata from MCD file in XML format."""
        return self._xml_parser.get_mcd_xml()

    @property
    def mcd_filename(self):
        """Name of the open MCD file"""
        return self._fh.name

    def get_acquisition_data(self, acquisition_id: int):
        """Returns AcquisitionData object with binary image data for given acquisition ID"""
        acquisition = self.session.acquisitions.get(acquisition_id)
        data = self._get_acquisition_raw_data(acquisition)
        if data is not None:
            image_data = reshape_long_2_cyx(data, is_sorted=True)
            # Drop first three channels X, Y, Z
            image_data = image_data[3:]
        else:
            image_data = None
            acquisition.is_valid = False
            logger.warning(f"Error reading MCD acquisition: {acquisition_id}")
        return AcquisitionData(acquisition, image_data)

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
        total_n_channels = acquisition.n_channels + 3
        data_size = end_offset - start_offset + 1
        data_nrows = int(data_size / (total_n_channels * int(acquisition.metadata.get(const.VALUE_BYTES))))
        if data_nrows <= 0:
            logger.error(f"Acquisition {acquisition.meta_name} is emtpy")
            return None
            # raise AcquisitionError(f"Acquisition {acquisition.id} is emtpy!")

        data = np.memmap(
            self._fh, dtype=np.float32, mode="r", offset=start_offset, shape=(data_nrows, total_n_channels)
        )
        return data

    def save_panorama_image(self, panorama_id: int, output_folder: str, output_filename: Optional[str] = None):
        """Save panorama image of the acquisition"""
        panorama_postfix = "pano"
        image_offset_fix = 161
        p = self.session.panoramas.get(panorama_id)
        img_start = int(p.metadata.get(const.IMAGE_START_OFFSET, 0)) + image_offset_fix
        img_end = int(p.metadata.get(const.IMAGE_END_OFFSET, 0)) + image_offset_fix

        if img_start - img_end == 0:
            return 0

        file_end = p.metadata.get(const.IMAGE_FORMAT, ".png").lower()

        if output_filename is None:
            output_filename = p.meta_name

        if not (output_filename.endswith(file_end)):
            output_filename += "_" + panorama_postfix + "." + file_end

        buf = self._get_buffer(img_start, img_end)
        with open(os.path.join(output_folder, output_filename), "wb") as f:
            f.write(buf)

    def save_slide_image(self, slide_id: int, output_folder: str, output_filename: Optional[str] = None):
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

        if output_filename is None:
            output_filename = s.meta_name
        if not (output_filename.endswith(slide_format)):
            output_filename += "_" + slide_postfix + slide_format

        buf = self._get_buffer(img_start, img_end)
        with open(os.path.join(output_folder, output_filename), "wb") as f:
            f.write(buf)

    def save_before_ablation_image(
        self, acquisition_id: int, output_folder: str, output_filename: Optional[str] = None
    ):
        return self._save_ablation_image(
            acquisition_id,
            output_folder,
            AblationImageType.BEFORE,
            const.BEFORE_ABLATION_IMAGE_START_OFFSET,
            const.BEFORE_ABLATION_IMAGE_END_OFFSET,
            output_filename,
        )

    def save_after_ablation_image(self, acquisition_id: int, output_folder: str, output_filename: Optional[str] = None):
        return self._save_ablation_image(
            acquisition_id,
            output_folder,
            AblationImageType.AFTER,
            const.AFTER_ABLATION_IMAGE_START_OFFSET,
            const.AFTER_ABLATION_IMAGE_END_OFFSET,
            output_filename,
        )

    def _save_ablation_image(
        self,
        acquisition_id: int,
        output_folder: str,
        ac_postfix: AblationImageType,
        start_offset: str,
        end_offset: str,
        output_filename: Optional[str] = None,
    ):
        image_offset_fix = 161
        image_format = ".png"
        a = self.session.acquisitions.get(acquisition_id)
        img_start = int(a.metadata.get(start_offset, 0)) + image_offset_fix
        img_end = int(a.metadata.get(end_offset, 0)) + image_offset_fix
        if img_end - img_start == 0:
            return False

        if output_filename is None:
            output_filename = a.meta_name
        buf = self._get_buffer(img_start, img_end)
        if not (output_filename.endswith(image_format)):
            output_filename += "_" + ac_postfix.value + image_format
        with open(os.path.join(output_folder, output_filename), "wb") as f:
            f.write(buf)
        return True

    def _get_buffer(self, start: int, stop: int):
        """Read binary data block from memory-mapped file"""
        self._fh.seek(start)
        buf = self._fh.read(stop - start)
        return buf

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

    def _get_mcd_xml(self, start_str: str = "<MCDSchema", stop_str: str = "</MCDSchema>", encoding: str = "utf-16-le"):
        with mmap.mmap(self._meta_fh.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            # MCD format documentation recommends searching from end for "<MCDSchema"
            start_offset = mm.rfind(start_str.encode(encoding))
            if start_offset == -1:
                raise ValueError(f"Invalid file {self.mcd_filename}: MCD XML start tag not found.")
            mm.seek(start_offset)
            stop_offset = mm.rfind(stop_str.encode(encoding))
            if stop_offset == -1:
                raise ValueError(f"Invalid file {self.mcd_filename}: MCD XML stop tag not found.")
            else:
                end_tag_length = len(stop_str)
                if encoding == "utf-16-le":
                    end_tag_length = end_tag_length * 2  # Multiply by 2 due to utf-16 encoding
                stop_offset += end_tag_length
            mcd_xml: str = mm.read(stop_offset - start_offset).decode(encoding)
            return mcd_xml

    def close(self):
        """Close file handlers."""
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

    parser = McdParser("/home/anton/Data/iMC_workshop_2019/20190919_FluidigmBrCa_SE/20190919_FluidigmBrCa_SE.mcd")

    print(timeit.default_timer() - tic)
