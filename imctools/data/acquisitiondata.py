import logging
import os
import re
from typing import Optional, Sequence

import numpy as np
import tifffile
from xtiff import to_tiff

from imctools import __version__
from imctools.data import Acquisition
from imctools.io.utils import get_ome_xml, OME_TIFF_SUFFIX

logger = logging.getLogger(__name__)


class AcquisitionData:
    """Container for IMC acquisition binary image data."""

    def __init__(self, acquisition: Acquisition, image_data: np.ndarray):
        self._acquisition = acquisition
        self._image_data = image_data

    @property
    def acquisition(self):
        return self._acquisition

    @property
    def image_data(self):
        """Binary image data as numpy array"""
        return self._image_data

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

    def get_image_by_index(self, index: int):
        """Get channel image by its index"""
        stack = self._get_image_stack_cyx(indices=[index])
        return stack[0]

    def get_image_by_name(self, name: str):
        """Get channel image by its name"""
        index = self.channel_names.index(name)
        return self.get_image_by_index(index)

    def get_image_by_label(self, label: str):
        """Get channel image by its label"""
        index = self.channel_labels.index(label)
        return self.get_image_by_index(index)

    def _get_image_stack_cyx(self, indices: Sequence[int] = None) -> Sequence[np.ndarray]:
        """Return the data reshaped as a stack of images"""
        if indices is None:
            indices = range(self.n_channels)
        img = [self.image_data[i] for i in indices]
        return img

    def save_ome_tiff(self, filename: str, names: Sequence[str] = None, xml_metadata: Optional[str] = None):
        """Save OME TIFF file

        Parameters
        ----------
        filename
            .ome.tiff file name
        names
            Channel names (metals / tags)
        xml_metadata
            Original MCD-XML metadata
        """
        if names is not None:
            order = self.acquisition.get_name_indices(names)
        else:
            order = [i for i in range(self.n_channels)]
        channel_names = [self.channel_labels[i] for i in order]
        channel_fluors = [self.channel_names[i] for i in order]
        creator = f"imctools {__version__}"
        data = np.array(self._get_image_stack_cyx(order), dtype=np.float32)
        to_tiff(
            data,
            filename,
            ome_xml_fun=get_ome_xml,
            channel_names=channel_names,
            channel_fluors=channel_fluors,
            creator=creator,
            acquisition_date=self.acquisition.start_timestamp.isoformat() if self.acquisition.start_timestamp else None,
            image_date=self.acquisition.start_timestamp,
            xml_metadata=xml_metadata,
        )

    def save_tiffs(self, output_folder: str, names: Sequence[str] = None, basename: str = None):
        """Save ImageJ TIFF files in a folder

        Parameters
        ----------
        output_folder
            Output folder
        names
            Channel names (metals / tags)
        basename
            Base file name
        """
        creator = f"imctools {__version__}"
        if names is not None:
            order = self.acquisition.get_name_indices(names)
        else:
            order = [i for i in range(self.n_channels)]
        for i in order:
            label = self.channel_labels[i]
            label = re.sub("[^a-zA-Z0-9()]", "-", label)
            name = self.channel_names[i]
            data = np.array(self.get_image_by_index(i), dtype=np.float32)
            if basename is None:
                basename = self.acquisition.description.rstrip(".ome.tiff") + "_"
            filename = os.path.join(output_folder, basename + label + "_" + name + ".tiff")
            tifffile.imwrite(filename, data, compress=0, imagej=True, bigtiff=False)

    def __repr__(self):
        return f"{self.__class__.__name__}(acquisition={self.acquisition})"
