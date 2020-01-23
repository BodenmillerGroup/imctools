import mmap
import os
from typing import BinaryIO

import numpy as np

import imctools.io.mcd.constants as const
from imctools.data import Acquisition
from imctools.io.errors import AcquisitionError
from imctools.io.mcd.mcdxmlparser import McdXmlParser
from imctools.io.utils import reshape_long_2_cyx


class McdParser:
    """Data parsing from Fluidigm MCD files

    The McdParser object should be closed using the close method

    """

    def __init__(self, filepath: str, file_handle: BinaryIO = None, meta_filename: str = None):
        """
        Parameters
        ----------

        filename
            Filename of an .mcd file
        file_handle
            File handle pointing to an open .mcd file

        """
        if file_handle is None:
            self._fh = open(filepath, mode="rb")
        else:
            self._fh = file_handle

        if meta_filename is None:
            self._meta_fh = self._fh
        else:
            self._meta_fh = open(meta_filename, mode="rb")

        footer = self._get_footer()
        public_xml_start = footer.find("<MCDPublic")
        self._xml = footer[:public_xml_start]

        self._xml_parser = McdXmlParser(self._xml, self._fh.name)
        self._session = self._xml_parser.session

    @property
    def filename(self):
        """Return the name of the open file

        """
        return self._fh.name

    @property
    def xml(self):
        return self._xml

    @property
    def session(self):
        return self._session

    def get_acquisition_buffer(self, acquisition_id: int):
        """Returns the raw buffer for the acquisition

        """
        ac = self.session.acquisitions.get(acquisition_id)
        start_offset = int(ac.metadata.get(const.DATA_START_OFFSET))
        end_offset = int(ac.metadata.get(const.DATA_END_OFFSET))
        data_size = end_offset - start_offset + 1
        self._fh.seek(start_offset)
        buffer = self._fh.read(data_size)
        return buffer

    def _get_acquisition_raw_data(self, acquisition: Acquisition):
        """Gets non-reshaped image data from the acquisition

        Parameters
        ----------
        acquisition
            Acquisition

        """
        start_offset = int(acquisition.metadata.get(const.DATA_START_OFFSET))
        end_offset = int(acquisition.metadata.get(const.DATA_END_OFFSET))
        total_n_channels = len(acquisition.channels)
        data_size = end_offset - start_offset + 1
        data_nrows = int(data_size / (total_n_channels * int(acquisition.metadata.get(const.VALUE_BYTES))))
        if data_nrows == 0:
            raise AcquisitionError(f"Acquisition {acquisition.id} emtpy!")

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

    def get_acquisition_with_image_data(self, acquisition_id: int, ac_description=None):
        """Returns an ImcAcquisition object corresponding to the ac_id

        """
        acquisition = self.session.acquisitions.get(acquisition_id)
        data = self._get_acquisition_raw_data(acquisition)
        img = reshape_long_2_cyx(data, is_sorted=True)
        acquisition.image_data = img
        return acquisition

    def save_panorama_image(self, panorama_id: int, out_folder: str, fn_out=None):
        """Save panorama image of the acquisition

        """
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
        self, acquisition_id: int, out_folder: str, ac_postfix: str, start_offset: str, end_offset: str, fn_out=None
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
        with open(os.path.join(out_folder, fn_out), "wb") as f:
            f.write(buf)

    def save_meta_xml(self, out_folder: str):
        self._xml_parser.save_meta_xml(out_folder)

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
    # filename = "/home/anton/Data/20170905_Fluidigmworkshopfinal_SEAJa/20170905_Fluidigmworkshopfinal_SEAJa.mcd"
    with McdParser(filename) as parser:
        ac = parser.get_acquisition_with_image_data(1)
        ac.save_ome_tiff("/home/anton/Downloads/test_v2.ome.tiff")
        parser.save_panorama_image(1, "/home/anton/Downloads")
        parser.save_slide_image(0, "/home/anton/Downloads")
        parser.save_meta_xml("/home/anton/Downloads")
        parser.save_before_ablation_image(1, "/home/anton/Downloads")
        parser.save_after_ablation_image(1, "/home/anton/Downloads")
        parser.session.save("/home/anton/Downloads/test.json")
    print(timeit.default_timer() - tic)
