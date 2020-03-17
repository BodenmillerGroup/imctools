import xml.etree.ElementTree as ET
from typing import Optional

import tifffile

from imctools.data import Acquisition, Channel
from imctools.data.acquisitiondata import AcquisitionData
from imctools.io.utils import OME_TIFF_SUFFIX


class OmeTiffParser:
    """Parser of MCD compatible .OME-TIFF files.

     Allows to get a single IMC acquisition from a single OME-TIFF file.
     """

    def __init__(self, filepath: str, slide_id: int = 0, channel_id_offset: int = 0):
        self._filepath = filepath
        self._slide_id = slide_id
        self._channel_id_offset = channel_id_offset
        self._acquisition_data = self._parse_acquisition(filepath)

    @property
    def origin(self):
        return "ome.tiff"

    @property
    def filepath(self):
        return self._filepath

    def get_mcd_xml(self) -> Optional[str]:
        """Original (raw) metadata from MCD file in XML format."""
        return self._mcd_xml

    def get_acquisition_data(self):
        """Returns AcquisitionData object with binary image data"""
        return self._acquisition_data

    @staticmethod
    def extract_acquisition_id(filepath: str):
        """Extract acquisition ID from source OME-TIFF filepath.

        Filename should end with a numeric symbol!

        Parameters
        ----------
        filepath
            Input OME-TIFF filepath
        """
        return int(filepath.rstrip(OME_TIFF_SUFFIX).split("_")[-1].lstrip("a"))

    def _parse_acquisition(self, filepath: str):
        image_data, ome_xml = OmeTiffParser._read_file(filepath)
        image_name, channel_names, channel_labels, self._mcd_xml = OmeTiffParser._parse_ome_xml(ome_xml)

        max_x = image_data.shape[2]
        max_y = image_data.shape[1]

        # TODO: implement a proper signal type extraction
        signal_type = "Dual"

        # Extract acquisition id from OME-TIFF file name
        acquisition_id = OmeTiffParser.extract_acquisition_id(filepath)

        # Offset should be 0 as we already got rid of 'X', 'Y', 'Z' channels!
        acquisition = Acquisition(
            self._slide_id,
            acquisition_id,
            self.origin,
            filepath,
            max_x,
            max_y,
            signal_type=signal_type,
            description=image_name,
        )

        for i in range(len(channel_names)):
            channel = Channel(acquisition.id, self._channel_id_offset, i, channel_names[i], channel_labels[i])
            self._channel_id_offset += 1
            channel.acquisition = acquisition
            acquisition.channels[channel.id] = channel

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


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()

    with OmeTiffParser(
        "/home/anton/Downloads/imc_folder/20190919_FluidigmBrCa_SE/20190919_FluidigmBrCa_SE_s0_a1_ac.ome.tiff"
    ) as parser:
        ac = parser.get_acquisition_data()
        pass

    print(timeit.default_timer() - tic)
