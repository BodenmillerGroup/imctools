from pathlib import Path
from typing import Union

import tifffile

from imctools.data import Session
from imctools.data.acquisitiondata import AcquisitionData
from imctools.io.utils import OME_TIFF_SUFFIX, SCHEMA_XML_SUFFIX, SESSION_JSON_SUFFIX


class ImcParser:
    """IMC folder parser."""

    def __init__(self, input_dir: Union[str, Path]):
        if isinstance(input_dir, str):
            input_dir = Path(input_dir)
        self.input_dir = input_dir

        session_json = str(next(input_dir.glob(f"*{SESSION_JSON_SUFFIX}")))
        self._session = Session.load(session_json)

    @property
    def origin(self):
        return "imc"

    @property
    def session(self):
        return self._session

    def get_mcd_xml(self):
        """Original (raw) metadata from MCD file in XML format."""
        xml_metadata_filename = self.session.metaname + SCHEMA_XML_SUFFIX
        with open(self.input_dir / xml_metadata_filename, "rt") as f:
            return f.read()

    def get_acquisition_data(self, acquisition_id: int):
        """Returns AcquisitionData object with binary image data"""
        acquisition = self.session.acquisitions.get(acquisition_id)
        if acquisition is None:
            return None
        filename = acquisition.metaname + OME_TIFF_SUFFIX
        image_data = ImcParser._read_file(self.input_dir / filename)
        acquisition_data = AcquisitionData(acquisition, image_data)
        return acquisition_data

    @staticmethod
    def _read_file(filepath: Path):
        with tifffile.TiffFile(filepath) as tif:
            return tif.asarray(out="memmap")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()

    with ImcParser("/home/anton/Downloads/imc_from_mcd") as parser:
        session = parser.session
        xml = parser.get_mcd_xml()
        ac = parser.get_acquisition_data(1)
        img = ac.get_image_by_index(1)

    print(timeit.default_timer() - tic)
