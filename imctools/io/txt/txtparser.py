import re
from pathlib import Path
from typing import Sequence, Union

import numpy as np
import pandas as pd

from imctools.data import Acquisition, Channel
from imctools.data.acquisitiondata import AcquisitionData
from imctools.io.utils import reshape_long_2_cyx

TXT_FILE_EXTENSION = ".txt"


class TxtParser:
    """Parser of MCD compatible .txt files.

    Allows to get a single IMC acquisition from a single TXT file.
    """

    def __init__(self, filepath: Union[str, Path], slide_id: int = 0, channel_id_offset: int = 0):
        if isinstance(filepath, str):
            filepath = Path(filepath)
        self._filepath = filepath
        self._slide_id = slide_id
        self._channel_id_offset = channel_id_offset
        self._acquisition_data = self._parse_acquisition(filepath)

    @property
    def origin(self):
        return "txt"

    @property
    def filepath(self):
        return self._filepath

    def get_acquisition_data(self):
        """Returns AcquisitionData object with binary image data"""
        return self._acquisition_data

    def _parse_acquisition(self, filepath: Path):
        long_data, channel_names, channel_labels = TxtParser._parse_csv(filepath)
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
        acquisition_id = TxtParser.extract_acquisition_id(filepath)

        # Don't forget to change slide ID if needed!
        acquisition = Acquisition(
            self._slide_id, acquisition_id, self.origin, str(filepath), max_x, max_y, signal_type=signal_type
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
    def extract_acquisition_id(filepath: Union[str, Path]):
        """Extract acquisition ID from source TXT filepath.

        Filename should end with a numeric symbol!

        Parameters
        ----------
        filepath
            Input TXT filepath.
        """
        if isinstance(filepath, str):
            filepath = Path(filepath)
        return int(filepath.stem.split("_")[-1])

    @staticmethod
    def _parse_csv(filepath: Path):
        """Parse CSV file.

        Parameters
        ----------
        filepath
            Input filepath.
        """
        header_cols = pd.read_csv(filepath, sep="\t", nrows=0).columns
        expected_cols = ("Start_push", "End_push", "Pushes_duration", "X", "Y", "Z")
        if tuple(header_cols[:6]) != expected_cols or len(header_cols) <= 6:
            raise ValueError(
                f"'{str(filepath)}' is not valid IMC text data (expected first 6 columns: {expected_cols}, plus intensity data)."
            )
        # Actual read, dropping irrelevant columns and casting image data to float32
        df = pd.read_csv(
            filepath,
            sep="\t",
            usecols=lambda c: c not in ("Start_push", "End_push", "Pushes_duration"),
            dtype={c: np.float32 for c in header_cols[3:]},
        )
        data = df.values
        channel_labels = [col for col in header_cols if col not in ("Start_push", "End_push", "Pushes_duration")]
        channel_names = channel_labels[:]
        channel_names[3:] = TxtParser._extract_channel_names(channel_names[3:])
        return data, channel_names, channel_labels

    @staticmethod
    def _extract_channel_names(names: Sequence[str]):
        """
        Returns channel names in Fluidigm compatible format, i.e. Y(89) or ArAr(80).

        Parameters
        ----------
        names
            CSV file column names.
        """
        # find which version it is
        names = [n.strip("\r") for n in names]
        names = [n.strip("\n") for n in names]
        names = [n.strip() for n in names]
        # string of sort asbsdf(mn123di)
        if names[0].rfind(")") == (len(names[0]) - 1):
            # get m123di

            names = [n[(n.rfind("(") + 1) : (n.rfind(")"))] for n in names]

        # string of sort aasbas_mn123
        elif "_" in names[0]:
            names = [n.split("_")[-1] for n in names]

        # else do nothing
        else:
            return names

        # else there is the bug where (123123di)
        names = [n.rstrip("di") for n in names]
        names = [n.rstrip("Di") for n in names]
        if names[0][0].isdigit():
            names = [n[(int(len(n) / 2)) :] for n in names]

        return names

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()

    with TxtParser(
        "/home/anton/Downloads/20170905_Fluidigmworkshopfinal_SEAJa/Site1_0_ROI_1_upperleft_0.txt"
    ) as parser:
        ac = parser.get_acquisition_data()
        pass

    print(timeit.default_timer() - tic)
