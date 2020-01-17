import re
from typing import Sequence

import numpy as np
import pandas as pd

from imctools.io.imc_acquisition import ImcAcquisition
from imctools.io.utils import reshape_long_2_cyx


class TxtParser:
    """
    Parses an IMC .txt file
    """

    def __init__(self, filename: str):
        self.filename = filename
        self.origin = "txt"
        self.data, self.channel_names, self.channel_labels = self.parse_csv(filename)

    @property
    def ac_id(self):
        ac_id = fn.rstrip(".txt").split("_")[-1]
        return ac_id

    def get_imc_acquisition(self):
        """
        Returns the imc acquisition object
        :return:
        """
        img = reshape_long_2_cyx(self.data, is_sorted=True)
        return ImcAcquisition(
            self.ac_id,
            self.filename,
            img,
            self.channel_names,
            self.channel_labels,
            metadata=None,
            description=None,
            origin=self.origin,
            offset=3,
        )

    def parse_csv(self, filename):
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
        channel_names = self._extract_channel_names(names)
        channel_labels = self._extract_channel_labels(names)
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
    imc_txt = TxtParser(fn)
    imc_ac = imc_txt.get_imc_acquisition()
    imc_ac.save_image("/home/anton/Downloads/test_2x.ome.tiff")
    print(timeit.default_timer() - tic)
