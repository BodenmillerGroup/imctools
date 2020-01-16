import numpy as np
import pandas as pd
import xarray as xr
import xmltodict

import re
from pathlib import Path
from typing import Union, List, Sequence, Generator
import mmap
import struct


class ROIData:
    """Represents image data (individual ROI) in long form. Meant to be instantiated by
    file readers and convert long-form image data into data arrays behind the scenes."""

    def __init__(self, df: pd.DataFrame, name, attrs=None):
        """df is a long-form dataarray with columns zero-indexed X, Y as a MultiIndex with
        additional columns as channel intensities."""
        self.df = df
        self.name = name
        self.attrs = attrs

    @classmethod
    def from_txt(cls, path):
        """Initialize image from .txt file."""
        # First pass to validate text file columns are consistent with IMC data
        header_cols = pd.read_csv(path, sep="\t", nrows=0).columns
        expected_cols = ("Start_push", "End_push", "Pushes_duration", "X", "Y", "Z")
        if tuple(header_cols[:6]) != expected_cols or len(header_cols) <= 6:
            raise ValueError(
                f"'{str(path)}' is not valid IMC text data (expected first 6 columns: {expected_cols}, plus intensity data)."
            )
        # Actual read, dropping irrelevant columns and casting image data to float32
        txt = pd.read_csv(
            path,
            sep="\t",
            usecols=lambda c: c not in ("Start_push", "End_push", "Pushes_duration", "Z"),
            index_col=["X", "Y"],
            dtype={c: np.float32 for c in header_cols[6:]},
        )
        # Rename columns to be consistent with .mcd format
        txt.columns = [_parse_txt_channel(col) for col in txt.columns]
        return cls(txt, Path(path).stem)

    def _df_to_array(self):
        xsz, ysz = self.df.index.to_frame().max()[["X", "Y"]] + 1
        csz = len(self.df.columns)
        # Ensure X/Y are fully specified, and fill in missing indices if needed
        multiindex = pd.MultiIndex.from_product([range(xsz), range(ysz)], names=["X", "Y"])
        # This will create nan rows if certain x/y combinations are missing:
        df_fill = self.df.reindex(multiindex)
        # Sort values by ascending Y, then X, so that we can reshape in C index order
        return df_fill.sort_values(["Y", "X"]).values.reshape((ysz, xsz, csz))

    def as_dataarray(self, fill_missing):
        # Reshape long-form data to image
        arr = self._df_to_array()
        # Try to fill missing values if necessary
        nan_mask = np.isnan(arr)
        if fill_missing is None and nan_mask.sum() > 0:
            raise ValueError("Image data is missing values. Try specifying 'fill_missing'.")
        arr[np.isnan(arr)] = fill_missing
        return xr.DataArray(
            arr,
            name=self.name,
            dims=("y", "x", "c"),
            coords={"x": range(arr.shape[1]), "y": range(arr.shape[0]), "c": self.df.columns.tolist()},
            attrs=self.attrs,
        )


def _parse_txt_channel(header: str) -> str:
    """Extract channel and label from text headers and return channels as formatted by
    MCDViewer. e.g. 80ArAr(ArAr80Di) -> ArAr(80)_80ArAr
    Args:
        headers: channel text header
    Returns:
        Channel header renamed to be consistent with MCD Viewer output
    """
    label, metal, mass = re.findall(r"(.+)\(([a-zA-Z]+)(\d+)Di\)", header)[0]
    return f"{metal}({mass})_{label}"


def read_txt(path: Union[Path, str], fill_missing: float = -1) -> xr.DataArray:
    """Read a Fluidigm IMC .txt file and returns the image data as an xarray DataArray.
    This is a convenience function which avoids instantiating ROIData.
    Args:
        path: path to IMC .txt file.
        fill_missing: value to use to fill in missing image data. If not specified,
            an error will be raised if there is missing image data.
    Returns:
        An xarray DataArray containing multichannel image data.
    Raises:
        ValueError: File is not valid IMC text data or missing values."""
    return ROIData.from_txt(path).as_dataarray(fill_missing)


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()
    result = read_txt(
        "/home/anton/Downloads/for Anton/IMMUcan_Batch20191023_10032401-HN-VAR-TIS-01-IMC-01_AC2/IMMUcan_Batch20191023_10032401-HN-VAR-TIS-01-IMC-01_AC2_pos1_6_6.txt"
    )
    print(timeit.default_timer() - tic)
