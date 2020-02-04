import os
from pathlib import Path

import tifffile

from imctools.data import Session
from imctools.io.imc.imcwriter import JSON_META_SUFFIX, XML_META_SUFFIX, OME_TIFF_SUFFIX
from imctools.io.parserbase import ParserBase


class ImcParser(ParserBase):
    """IMC folder parser.

    The ImcParser object should be closed using the close method
    """

    def __init__(self, input_dir: str):
        ParserBase.__init__(self)
        self.input_dir = input_dir

        session_json = str(next(Path(input_dir).glob("*" + JSON_META_SUFFIX)))
        self._session = Session.load(session_json)

    @property
    def origin(self):
        return "imc"

    @property
    def session(self):
        return self._session

    def get_mcd_xml(self):
        """Original (raw) metadata from MCD file in XML format."""
        xml_metadata_filename = self.session.meta_name + XML_META_SUFFIX
        with open(os.path.join(self.input_dir, xml_metadata_filename), "rt") as f:
            return f.read()

    def get_acquisition_image_data(self, acquisition_id: int):
        """Returns an Acquisition object with relevant image data"""
        ac = self.session.acquisitions.get(acquisition_id)
        filename = ac.meta_name + OME_TIFF_SUFFIX
        ac.image_data = ImcParser._read_file(os.path.join(self.input_dir, filename))
        return ac

    @staticmethod
    def _read_file(filepath: str):
        with tifffile.TiffFile(filepath) as tif:
            return tif.asarray(out="memmap")


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()

    with ImcParser("/home/anton/Downloads/imc_from_mcd") as parser:
        session = parser.session
        xml = parser.get_mcd_xml()
        ac = parser.get_acquisition_image_data(1)
        img = ac.get_image_by_index(1)

    print(timeit.default_timer() - tic)
