import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence, Optional

import numpy as np
import pandas as pd

from imctools import __version__
from imctools.data import Acquisition, Channel, Slide, Session
from imctools.io.parserbase import ParserBase
from imctools.io.utils import reshape_long_2_cyx


class TxtParser(ParserBase):
    """MCD compatible .txt file parser.

    Allows to get a single IMC acquisition from a single TXT file.
    """

    def __init__(self, filepath: str, parent_slide: Optional[Slide] = None):
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
        return "txt"

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

    def _parse_acquisition(self, filename: str):
        long_data, channel_names, channel_labels = TxtParser._parse_csv(filename)
        image_data = reshape_long_2_cyx(long_data, is_sorted=True)

        # Delete 'X', 'Y', 'Z' channels data
        image_data = np.delete(image_data, [0, 1, 2], axis=0)
        channel_names = channel_names[3:]
        channel_labels = channel_labels[3:]

        max_x = image_data.shape[2]
        max_y = image_data.shape[1]

        # Extract signal type from CSV header
        signal_type = "Dual" if channel_labels[0][-3:-1] == "Di" else ""

        # Extract acquisition id from txt file name
        acquisition_id = int(filename.rstrip(".txt").split("_")[-1])

        slide = self.session.slides.get(0)

        # Offset should be 0 as we already got rid of 'X', 'Y', 'Z' channels!
        acquisition = Acquisition(
            slide.id,
            acquisition_id,
            max_x,
            max_y,
            signal_type=signal_type,
            description=filename
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
    def _parse_csv(filename: str):
        header_cols = pd.read_csv(filename, sep="\t", nrows=0).columns
        expected_cols = ("Start_push", "End_push", "Pushes_duration", "X", "Y", "Z")
        if tuple(header_cols[:6]) != expected_cols or len(header_cols) <= 6:
            raise ValueError(
                f"'{str(filename)}' is not valid IMC text data (expected first 6 columns: {expected_cols}, plus intensity data)."
            )
        # Actual read, dropping irrelevant columns and casting image data to float32
        df = pd.read_csv(
            filename,
            sep="\t",
            usecols=lambda c: c not in ("Start_push", "End_push", "Pushes_duration"),
            dtype={c: np.float32 for c in header_cols[3:]},
        )
        data = df.values
        names = [col for col in header_cols if col not in ("Start_push", "End_push", "Pushes_duration")]
        channel_names = TxtParser._extract_channel_names(names)
        channel_labels = TxtParser._extract_channel_labels(names)
        return data, channel_names, channel_labels

    @staticmethod
    def _extract_channel_names(names: Sequence[str]):
        """
        Returns channel names in Fluidigm compatible format, i.e. Y(89) or ArAr(80)

        Parameters
        ----------
        names
            CSV file column names
        """
        r = re.compile("^.*\((.*?)\)[^(]*$")
        r_number = re.compile("\d+")
        result = []
        for name in names:
            n = r.sub("\g<1>", name.strip("\r").strip("\n").strip()).rstrip("di").rstrip("Di")
            metal_name = r_number.sub("", n)
            metal_mass = n.replace(metal_name, "")
            metal_mass = f"({metal_mass})" if metal_mass != "" else ""
            result.append(f"{metal_name}{metal_mass}")
        return result

    @staticmethod
    def _extract_channel_labels(names: Sequence[str]):
        """Returns channel labels in Fluidigm compatible format, i.e. Myelope_276((2669))Y89(Y89Di) or 80ArAr(ArAr80Di)

        Parameters
        ----------
        names
            CSV file column names
        """
        return [name.strip("\r").strip("\n").strip() for name in names]


if __name__ == "__main__":
    import timeit
    from imctools.io.imc.imcwriter import ImcWriter

    tic = timeit.default_timer()
    parser = TxtParser("/home/anton/Data/20190731_ZTMA256.1_slide2_TH/Row_1_14_A3_7.txt")
    imc_writer = ImcWriter(parser.session)
    imc_writer.write_to_folder("/home/anton/Downloads/imc_from_txt")
    print(timeit.default_timer() - tic)
