import logging
import os

from imctools.data import Session

logger = logging.getLogger(__name__)


class ImcWriter:
    """Write IMC session data to IMC folder structure"""

    def __init__(self, session: Session, original_xml_metadata: str = None):
        self.session = session
        self.original_xml_metadata = original_xml_metadata

    def write_to_folder(self, output_folder: str):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        self.session.save(os.path.join(output_folder, self.session.meta_name + ".json"))

        if self.original_xml_metadata is not None:
            with open(os.path.join(output_folder, self.session.meta_name + ".xml"), "wt") as f:
                f.write(self.original_xml_metadata)

        for acquisition in self.session.acquisitions.values():
            acquisition.save_ome_tiff(os.path.join(output_folder, acquisition.meta_name + ".ome.tiff"))
