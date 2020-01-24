import os
import uuid
from datetime import datetime
from typing import Sequence
import xml.etree.ElementTree as ET

import tifffile

from imctools import __version__
from imctools.data import Acquisition, Session, Slide, Channel
from imctools.io.parserbase import ParserBase


class ImcParser(ParserBase):
    """Data parsing from OME-TIFF files

    """

    def __init__(self, input_dir: str):
        ParserBase.__init__(self)
        self.input_dir = input_dir

        self._session =

    @property
    def origin(self):
        return "ome.tiff"

    @property
    def session(self):
        return self._session

    def _find_session_name(self):
        filenames = [f for f in os.listdir(self.input_dir)]
        return os.path.commonprefix(filenames).rstrip("_")

    def parse_files(self, filenames: Sequence[str]):
        for filename in filenames:
            self._parse_acquisition(os.path.join(self.input_dir, filename))

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
            slide.id, acquisition_id, max_x, max_y, signal_type, "Float", description=image_name, offset=0
        )
        acquisition.image_data = image_data
        acquisition.slide = slide
        slide.acquisitions[acquisition.id] = acquisition
        self.session.acquisitions[acquisition.id] = acquisition

        for i in range(len(channel_names)):
            channel = Channel(acquisition.id, self._channel_id_offset, i, channel_names[i], channel_labels[i])
            self._channel_id_offset = self._channel_id_offset + 1
            channel.acquisition = acquisition
            acquisition.channels[channel.id] = channel
            self.session.channels[channel.id] = channel

        # Calculate channels intensity range
        for ch in acquisition.channels.values():
            img = acquisition.get_image_by_name(ch.name)
            ch.min_intensity = round(float(img.min()), 4)
            ch.max_intensity = round(float(img.max()), 4)

    @staticmethod
    def _parse_ome_tiff_metadata(xml: str):
        ome = ET.fromstring(xml)
        ns = '{' + ome.tag.split('}')[0].strip('{') + '}'

        img = ome.find(ns + 'Image')
        pixels = img.find(ns + 'Pixels')
        channels = pixels.findall(ns + 'Channel')
        chan_dict = {int(chan.attrib['ID'].split(':')[2]):
                         (chan.attrib['Name'], chan.attrib['Fluor']) for chan in channels}

        image_name = img.attrib['Name']
        channel_names = [chan_dict[i][1] for i in range(len(channels))]
        channel_labels = [chan_dict[i][0] for i in range(len(channels))]

        return image_name, channel_names, channel_labels

    @staticmethod
    def _read_file(filepath: str):
        with tifffile.TiffFile(filepath) as tif:
            data = tif.asarray(out="memmap")
            try:
                ome = tif.pages[0].tags['ImageDescription'].value
            except:
                ome = tif.pages[0].tags['image_description'].value
            return data, ome


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()
    parser = OmeTiffParser("/home/anton/Data/20190723_measurements/ImcSegmentationPipeline/output/ometiff/20190723_SilverNitrate_Tonsil_TH")
    parser.session.save(os.path.join("/home/anton/Downloads", parser.session.meta_name + ".json"))
    print(timeit.default_timer() - tic)
