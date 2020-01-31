import logging
import os

from imctools.io.parserbase import ParserBase

logger = logging.getLogger(__name__)


class ImcWriter:
    """Write IMC session data to IMC folder structure."""

    def __init__(self, parser: ParserBase):
        """
        Parameters
        ----------
        parser
            Instance of specific parser, i.e. McdParser, TxtParser, etc.
        """
        self._parser = parser

    @property
    def parser(self):
        """Parser instance"""
        return self._parser

    def save_imc_folder(self, output_folder: str):
        """Save IMC session data into folder with IMC-compatible structure

        Parameters
        ----------
        output_folder
            Output directory where all files will be stored
        """
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        session = self.parser.session
        session.save(os.path.join(output_folder, session.meta_name + ".json"))

        # Save XML metadata if available
        if self.parser.xml_metadata is not None:
            with open(os.path.join(output_folder, session.meta_name + ".xml"), "wt") as f:
                f.write(self.parser.xml_metadata)

        # Save acquisition images in OME-TIFF format
        for acquisition in session.acquisitions.values():
            acquisition.save_ome_tiff(os.path.join(output_folder, acquisition.meta_name + ".ome.tiff"), xml_metadata=self.parser.xml_metadata)

        # Save parser-specific artifacts, like panorama images, before/after ablation images, etc.
        self.parser.save_artifacts(output_folder)
