import re
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

from imctools import __version__
from imctools.data import Session, Slide, Acquisition, Channel
from imctools.io.utils import reshape_long_2_cyx


class TxtParser:
    """
    Parses IMC .txt file

    """
    def __init__(self, filepath: str):
        self.origin = "txt"
        self.filepath = filepath

        data, channel_names, channel_labels = self.parse_csv(self.filepath)
        original_id = self.filepath.rstrip(".txt").split("_")[-1]
        filename = Path(self.filepath).name

        session = Session(filename, __version__, self.origin, self.filepath)
        slide = Slide(session.id, "0")
        session.slides[slide.original_id] = slide

        img = reshape_long_2_cyx(data, is_sorted=True)
        acquisition = Acquisition(
            slide.original_id,
            original_id,
            img,
            channel_names,
            channel_labels,
            None,
            self.origin,
            3
        )
        # slide.acquisitions[acquisition.original_id] = acquisition
        session.acquisitions[acquisition.original_id] = acquisition
        for i, channel_name in enumerate(channel_names):
            channel_original_id = str(i + 1)
            channel = Channel(acquisition.original_id, channel_original_id, channel_name, channel_labels[i])
            # acquisition.channels[channel_original_id] = channel
            session.channels[channel_original_id] = channel

        self._session = session

    @property
    def session(self):
        return self._session

    @staticmethod
    def parse_csv(filepath: str):
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
        r = re.compile(r"^.*\((.*?)\)[^(]*$")
        r_number = re.compile(r"\d+")
        result = []
        for name in names:
            n = r.sub(r"\g<1>", name.strip("\r").strip("\n").strip()).rstrip("di").rstrip("Di")
            metal_name = r_number.sub("", n)
            metal_mass = n.replace(metal_name, "")
            metal_mass = f"({metal_mass})" if metal_mass != "" else ""
            result.append(f"{metal_name}{metal_mass}")
        return result

    @staticmethod
    def _extract_channel_labels(names: Sequence[str]):
        """
        Returns channel labels in Fluidigm compatible format, i.e. Myelope_276((2669))Y89(Y89Di) or 80ArAr(ArAr80Di)

        Parameters
        ----------
        names
            CSV file column names

        """
        return [name.strip("\r").strip("\n").strip() for name in names]


if __name__ == "__main__":
    import timeit

    fn = "/home/anton/Downloads/for Anton/IMMUcan_Batch20191023_10032401-HN-VAR-TIS-01-IMC-01_AC2/IMMUcan_Batch20191023_10032401-HN-VAR-TIS-01-IMC-01_AC2_pos1_6_6.txt"
    tic = timeit.default_timer()
    parser = TxtParser(fn)
    session = parser.session
    # session.slides["0"].acquisitions["6"].save_image("/home/anton/Downloads/test_2x.ome.tiff")
    session.save("/home/anton/Downloads/test.yaml")
    print(timeit.default_timer() - tic)
