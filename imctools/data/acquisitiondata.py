import logging
import os
import re
from typing import Optional, Sequence

import numpy as np
import tifffile
from xtiff import to_tiff

from imctools import __version__
from imctools.data import Acquisition
from imctools.io.utils import get_ome_xml

logger = logging.getLogger(__name__)


class AcquisitionData:
    """Container for IMC acquisition binary image data."""

    def __init__(self, acquisition: Acquisition, image_data: np.ndarray):
        self._acquisition = acquisition
        self._image_data = image_data

    @property
    def acquisition(self):
        """Acquisition metadata"""
        return self._acquisition

    @property
    def image_data(self):
        """Binary image data as numpy array"""
        return self._image_data

    def to_xarray(self):
        """Get binary image data as xarray"""
        try:
            import xarray as xr
            return xr.DataArray(self._image_data, dims=("fluor", "x", "y"), coords={"fluor": self.channel_names})
        except ImportError:
            raise ImportError("Please install 'xarray' package first.")

    @property
    def is_valid(self):
        return self._acquisition.is_valid

    @property
    def n_channels(self):
        """Number of channels"""
        return self._acquisition.n_channels

    @property
    def channel_names(self):
        """Channel names"""
        return self._acquisition.channel_names

    @property
    def channel_labels(self):
        """Channel labels"""
        return self._acquisition.channel_labels

    @property
    def channel_masses(self):
        """Channel masses"""
        return self._acquisition.channel_masses

    def get_image_stack_by_indices(self, indices: Sequence[int]):
        """Get image stack by channel indices"""
        stack = self._get_image_stack_cyx(indices=indices)
        return stack

    def get_image_by_index(self, index: int):
        """Get channel image by its index"""
        stack = self._get_image_stack_cyx(indices=[index])
        return stack[0]

    def get_image_stack_by_names(self, names: Sequence[str]):
        """Get image stack by channel names"""
        indices = [self.channel_names.index(name) for name in names]
        return self.get_image_stack_by_indices(indices)

    def get_image_by_name(self, name: str):
        """Get channel image by its name"""
        index = self.channel_names.index(name)
        return self.get_image_by_index(index)

    def get_image_stack_by_labels(self, labels: Sequence[str]):
        """Get image stack by channel labels"""
        indices = [self.channel_labels.index(label) for label in labels]
        return self.get_image_stack_by_indices(indices)

    def get_image_by_label(self, label: str):
        """Get channel image by its label"""
        index = self.channel_labels.index(label)
        return self.get_image_by_index(index)

    def _get_image_stack_cyx(self, indices: Sequence[int] = None) -> Sequence[np.ndarray]:
        """Return the data reshaped as a stack of images"""
        if indices is None:
            indices = range(self.n_channels)
        return self.image_data[indices]

    def save_ome_tiff(
        self,
        filename: str,
        names: Sequence[str] = None,
        masses: Sequence[str] = None,
        xml_metadata: Optional[str] = None,
        dtype: Optional[object] = None,
    ):
        """Save OME TIFF file.

        Parameters
        ----------
        filename
            .ome.tiff file name.
        names
            Channel names (metals / tags).
        masses
            Channel masses.
        xml_metadata
            Original MCD-XML metadata.
        dtype
            Output numpy format.
        """
        if names is not None:
            order = self.acquisition.get_name_indices(names)
        elif masses is not None:
            order = self.acquisition.get_mass_indices(masses)
        else:
            order = [i for i in range(self.n_channels)]
        channel_labels = [self.channel_labels[i] for i in order]
        channel_names = [self.channel_names[i] for i in order]
        creator = f"imctools {__version__}"
        data = np.array(self._get_image_stack_cyx(order), dtype=dtype)
        to_tiff(
            data,
            filename,
            ome_xml_fun=get_ome_xml,
            channel_names=channel_labels,
            channel_fluors=channel_names,
            creator=creator,
            acquisition_date=self.acquisition.start_timestamp.isoformat() if self.acquisition.start_timestamp else None,
            image_date=self.acquisition.start_timestamp,
            xml_metadata=xml_metadata,
        )

    def save_tiff(
        self,
        filename: str,
        names: Sequence[str] = None,
        masses: Sequence[str] = None,
        add_sum=False,
        imagej=False,
        bigtiff=False,
        dtype: Optional[object] = None,
        compression: int = 0,
    ):
        if names is not None:
            order = self.acquisition.get_name_indices(names)
        elif masses is not None:
            order = self.acquisition.get_mass_indices(masses)
        else:
            order = [i for i in range(self.n_channels)]

        data = np.array(self._get_image_stack_cyx(order), dtype=dtype)

        if add_sum:
            img_sum = np.sum(data, axis=0)
            img_sum = np.reshape(img_sum, [1] + list(img_sum.shape))
            data = np.append(img_sum, data, axis=0)

        data = np.array(data, dtype=dtype)

        tifffile.imwrite(filename, data, compress=compression, imagej=imagej, bigtiff=bigtiff)

    def save_tiffs(
        self,
        output_folder: str,
        names: Sequence[str] = None,
        masses: Sequence[str] = None,
        basename: str = None,
        imagej=True,
        bigtiff=False,
        dtype: Optional[object] = None,
        compression: int = 0,
    ):
        """Save ImageJ TIFF files in a folder.

        Parameters
        ----------
        output_folder
            Output folder.
        names
            Channel names (metals / tags).
        masses
            Channel masses.
        basename
            Base file name.
        imagej
            Save TIFF file compatible with ImageJ format.
        bigtiff
            BigTIFF format.
        dtype
            Output numpy format.
        compression
            Compression level.
        """
        creator = f"imctools {__version__}"
        if names is not None:
            order = self.acquisition.get_name_indices(names)
        elif masses is not None:
            order = self.acquisition.get_mass_indices(masses)
        else:
            order = [i for i in range(self.n_channels)]
        for i in order:
            label = self.channel_labels[i]
            label = re.sub("[^a-zA-Z0-9()]", "-", label)
            name = self.channel_names[i]
            data = np.array(self.get_image_by_index(i), dtype=dtype)
            if basename is None:
                basename = self.acquisition.description.rstrip(".ome.tiff") + "_"
            filename = os.path.join(output_folder, basename + label + "_" + name + ".tiff")
            tifffile.imwrite(filename, data, compress=compression, imagej=imagej, bigtiff=bigtiff)

    def __repr__(self):
        return f"{self.__class__.__name__}(acquisition={self.acquisition})"
