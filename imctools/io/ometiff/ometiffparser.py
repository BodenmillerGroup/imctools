import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET

import tifffile

from imctools import __version__
from imctools.data import Acquisition, Session, Slide, Channel
from imctools.io.imc.imcwriter import ImcWriter
from imctools.io.parserbase import ParserBase


class OmeTiffParser(ParserBase):
    """MCD compatible OME-TIFF file parser.

     Allows to get a single IMC acquisition from a single OME-TIFF file.
     """

    def __init__(self, filepath: str, parent_slide: Optional[Slide] = None):
        ParserBase.__init__(self)
        self._filepath = filepath

        if parent_slide is not None:
            self._session = parent_slide.session
        else:
            split = Path(filepath).stem.split("_")
            session_name = "_".join(split[:-1])
            session_id = str(uuid.uuid4())
            session = Session(
                session_id,
                session_name,
                __version__,
                self.origin,
                filepath,
                datetime.now(timezone.utc),
            )
            slide = Slide(
                session.id,
                0,
                description=filepath
            )
            slide.session = session
            session.slides[slide.id] = slide
            self._session = session

        self._channel_id_offset = len(self.session.channels)
        self._acquisition = self._parse_acquisition(filepath)

    @property
    def origin(self):
        return "ome.tiff"

    @property
    def session(self):
        return self._session

    @property
    def acquisition(self):
        """IMC acquisition"""
        return self._acquisition

    @property
    def filepath(self):
        return self._filepath

    def save_imc_folder(self, output_folder: str):
        imc_writer = ImcWriter(self)
        imc_writer.save_imc_folder(output_folder)

    def _parse_acquisition(self, filename: str):
        image_data, ome = OmeTiffParser._read_file(filename)
        image_name, channel_names, channel_labels = OmeTiffParser._parse_ome_tiff_metadata(ome)

        max_x = image_data.shape[2]
        max_y = image_data.shape[1]

        # TODO: implement a proper signal type extraction
        signal_type = "Dual"

        # Extract acquisition id from txt file name
        acquisition_id = int(filename.rstrip(".ome.tiff").split("_")[-2].lstrip("a"))

        slide = self.session.slides.get(0)

        # Offset should be 0 as we already got rid of 'X', 'Y', 'Z' channels!
        acquisition = Acquisition(
            slide.id,
            acquisition_id,
            max_x,
            max_y,
            signal_type=signal_type,
            description=image_name
        )
        acquisition.image_data = image_data

        acquisition.slide = slide
        slide.acquisitions[acquisition.id] = acquisition
        slide.session.acquisitions[acquisition.id] = acquisition

        for i in range(len(channel_names)):
            channel = Channel(acquisition.id, self._channel_id_offset, i, channel_names[i], channel_labels[i])
            self._channel_id_offset = self._channel_id_offset + 1
            channel.acquisition = acquisition
            acquisition.channels[channel.id] = channel
            slide.session.channels[channel.id] = channel

        # Calculate channels intensity range
        for ch in acquisition.channels.values():
            img = acquisition.get_image_by_name(ch.name)
            ch.min_intensity = round(float(img.min()), 4)
            ch.max_intensity = round(float(img.max()), 4)

        return acquisition

    @staticmethod
    def _parse_ome_tiff_metadata(xml: str):
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

        return image_name, channel_names, channel_labels

    @staticmethod
    def _read_file(filepath: str):
        with tifffile.TiffFile(filepath) as tif:
            data = tif.asarray(out="memmap")
            try:
                ome = tif.pages[0].tags["ImageDescription"].value
            except:
                ome = tif.pages[0].tags["image_description"].value
            return data, ome


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()

    parser = OmeTiffParser(
        "/home/anton/Downloads/for Anton/new error/IMMUcan_Batch20191023_S-190701-00035 converted/IMMUcan_Batch20191023_S-190701-00035_s0_p15_r2_a2_ac.ome.tiff"
    )
    imc_writer = ImcWriter(parser)
    imc_writer.save_imc_folder("/home/anton/Downloads/imc_from_ometiff")

    print(timeit.default_timer() - tic)
