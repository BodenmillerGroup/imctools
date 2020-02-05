import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET

import tifffile

from imctools import __version__
from imctools.data import Acquisition, Session, Slide, Channel
from imctools.data.acquisitiondata import AcquisitionData
from imctools.io.utils import OME_TIFF_SUFFIX, SESSION_JSON_SUFFIX, SCHEMA_XML_SUFFIX


class OmeTiffParser:
    """MCD compatible OME-TIFF file parser.

     Allows to get a single IMC acquisition from a single OME-TIFF file.
     """

    def __init__(self, filepath: str, parent_slide: Optional[Slide] = None):
        self._filepath = filepath

        if parent_slide is not None:
            self._session = parent_slide.session
        else:
            split = Path(filepath).stem.split("_")
            session_name = "_".join(split[:-1])
            session_id = str(uuid.uuid4())
            session = Session(session_id, session_name, __version__, self.origin, filepath, datetime.now(timezone.utc),)
            slide = Slide(session.id, 0, description=filepath)
            slide.session = session
            session.slides[slide.id] = slide
            self._session = session

        self._channel_id_offset = len(self.session.channels)
        self._acquisition_data = self._parse_acquisition(filepath)

    @property
    def origin(self):
        return "ome.tiff"

    @property
    def session(self):
        return self._session

    @property
    def acquisition(self):
        """IMC acquisition"""
        return self._acquisition_data.acquisition

    @property
    def filepath(self):
        return self._filepath

    def get_mcd_xml(self) -> Optional[str]:
        """Original (raw) metadata from MCD file in XML format."""
        return self._mcd_xml

    def get_acquisition_data(self):
        """Returns AcquisitionData object with binary image data"""
        return self._acquisition_data

    def save_imc_folder(self, output_folder: str):
        """Save IMC session data into folder with IMC-compatible structure.

        This method usually should be overwritten by parser implementation.

        Parameters
        ----------
        output_folder
            Output directory where all files will be stored
        """
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        self.session.save(os.path.join(output_folder, self.session.meta_name + SESSION_JSON_SUFFIX))

        # Save XML metadata if available
        mcd_xml = self.get_mcd_xml()
        if mcd_xml is not None:
            with open(os.path.join(output_folder, self.session.meta_name + SCHEMA_XML_SUFFIX), "wt") as f:
                f.write(mcd_xml)

        self.get_acquisition_data().save_ome_tiff(
            os.path.join(output_folder, self.acquisition.meta_name + OME_TIFF_SUFFIX),
        )

    def _parse_acquisition(self, filename: str):
        image_data, ome_xml = OmeTiffParser._read_file(filename)
        image_name, channel_names, channel_labels, self._mcd_xml = OmeTiffParser._parse_ome_xml(ome_xml)

        max_x = image_data.shape[2]
        max_y = image_data.shape[1]

        # TODO: implement a proper signal type extraction
        signal_type = "Dual"

        # Extract acquisition id from txt file name
        acquisition_id = int(filename.rstrip(OME_TIFF_SUFFIX).split("_")[-1].lstrip("a"))

        slide = self.session.slides.get(0)

        # Offset should be 0 as we already got rid of 'X', 'Y', 'Z' channels!
        acquisition = Acquisition(slide.id, acquisition_id, max_x, max_y, signal_type=signal_type, description=image_name)
        acquisition.slide = slide
        slide.acquisitions[acquisition.id] = acquisition
        slide.session.acquisitions[acquisition.id] = acquisition

        for i in range(len(channel_names)):
            channel = Channel(acquisition.id, self._channel_id_offset, i, channel_names[i], channel_labels[i])
            self._channel_id_offset = self._channel_id_offset + 1
            channel.acquisition = acquisition
            acquisition.channels[channel.id] = channel
            slide.session.channels[channel.id] = channel

        acquisition_data = AcquisitionData(acquisition, image_data)
        # Calculate channels intensity range
        for ch in acquisition.channels.values():
            img = acquisition_data.get_image_by_name(ch.name)
            ch.min_intensity = round(float(img.min()), 4)
            ch.max_intensity = round(float(img.max()), 4)

        return acquisition_data

    @staticmethod
    def _parse_ome_xml(xml: str):
        ome = ET.fromstring(xml)
        ns = "{" + ome.tag.split("}")[0].strip("{") + "}"

        img = ome.find(ns + "Image")
        pixels = img.find(ns + "Pixels")
        channels = pixels.findall(ns + "Channel")
        chan_dict = {
            int(chan.attrib["ID"].split(":")[2]): (chan.attrib["Name"], chan.attrib["Fluor"]) for chan in channels
        }

        image_name = img.attrib["Name"]
        channel_names = [chan_dict[i][1] for i in range(len(channels))]
        channel_labels = [chan_dict[i][0] for i in range(len(channels))]

        structured_annotations = ome.find(ns + "StructuredAnnotations")
        xml_annotation = structured_annotations.find(ns + "XMLAnnotation")
        xml_annotation_value = xml_annotation.find(ns + "Value")
        original_metadata = xml_annotation_value.find(ns + "OriginalMetadata")
        original_metadata_value = original_metadata.find(ns + "Value")
        mcd_xml = original_metadata_value.text

        return image_name, channel_names, channel_labels, mcd_xml

    @staticmethod
    def _read_file(filepath: str):
        with tifffile.TiffFile(filepath) as tif:
            data = tif.asarray(out="memmap")
            try:
                ome_xml = tif.pages[0].tags["ImageDescription"].value
            except:
                ome_xml = tif.pages[0].tags["image_description"].value
            return data, ome_xml

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


def convert_ometiff_to_imc_folder(input_filename: str, output_folder: str):
    """High-level function for OME-TIFF-to-IMC conversion"""
    with OmeTiffParser(input_filename) as parser:
        parser.save_imc_folder(output_folder)


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()

    convert_ometiff_to_imc_folder(
        "/home/anton/Downloads/imc_from_mcd/IMMUcan_Batch20191023_10032401-HN-VAR-TIS-01-IMC-01_AC2_s0_a1_ac.ome.tiff",
        "/home/anton/Downloads/imc_from_ometiff",
    )

    print(timeit.default_timer() - tic)
