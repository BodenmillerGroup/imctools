from pathlib import Path
from typing import Sequence

import numpy as np
from xtiff import to_tiff

from imctools.io.utils import get_ome_channel_xml


class ImcAcquisition:
    """This defines the IMC acquisition base class

    This can be extended too e.g. read the data from a text file instead from a provided array.

    """

    def __init__(
        self,
        original_id: str,
        filepath: str,
        data: np.ndarray,
        channel_names: Sequence[str],
        channel_labels: Sequence[str],
        original_xml: str = None,
        description: str = None,
        origin: str = None,
        offset: int = 3,
    ):
        self.original_id = original_id
        self.filepath = filepath

        self._data = data
        self._offset = offset

        self._channel_names = channel_names
        self._channel_labels = channel_labels
        self.original_xml = original_xml
        self.description = description
        self.origin = origin

    @property
    def data(self):
        return self._data

    @property
    def filename(self):
        return Path(self.filepath).name

    @property
    def n_channels(self):
        """Number of channels

        Offset is taken into account (in order to skip X, Y, Z channels)

        """
        return len(self._data) - self._offset

    @property
    def shape(self):
        """Shape in cyx format (Channel, Y, X)

        """
        return self._data.shape

    @property
    def channel_names(self):
        """Channel names

        Offset is taken into account (in order to skip X, Y, Z channels)

        """
        return self._channel_names[self._offset :]

    @property
    def channel_labels(self):
        """Channel labels

        Offset is taken into account (in order to skip X, Y, Z channels)

        """
        return self._channel_labels[self._offset :] if self._channel_labels is not None else None

    @property
    def channel_masses(self):
        """Channel masses

        Offset is taken into account (in order to skip X, Y, Z channels)

        """
        return ["".join([m for m in metal if m.isdigit()]) for metal in self.channel_names]

    def get_name_indices(self, names: Sequence[str]):
        """Returns a list with the indices from names

        """
        order_dict = dict()
        for i, v in enumerate(self.channel_names):
            order_dict.update({v: i})

        return [order_dict[n] for n in names]

    def get_mass_indices(self, masses: Sequence[str]):
        """Returns the channel indices from the queried mass

        """
        order_dict = dict()
        for i, v in enumerate(self.channel_masses):
            order_dict.update({v: i})

        return [order_dict[m] for m in masses]

    def get_image_stack_cyx(self, indices: Sequence[int] = None, offset: int = None):
        """Return the data reshaped as a stack of images

        """
        if offset is None:
            offset = self._offset

        if indices is None:
            indices = range(self.n_channels)

        data = self._data
        img = [data[i + offset] for i in indices]
        return img

    def get_image_by_index(self, index: int):
        """Get channel image by its index

        """
        stack = self.get_image_stack_cyx(indices=[index])
        return stack[0]

    def get_image_by_name(self, name: str):
        """Get channel image by its name

        """
        index = self.channel_names.index(name)
        return self.get_image_by_index(index)

    def get_image_by_label(self, label: str):
        """Get channel image by its label

        """
        index = self.channel_labels.index(label)
        return self.get_image_by_index(index)

    def save_image(self, filename: str, names: Sequence[str] = None, masses: Sequence[str] = None):
        """Save OME TIFF file

        """
        if names is not None:
            order = self.get_name_indices(names)
        elif masses is not None:
            order = self.get_mass_indices(masses)
        else:
            order = [i for i in range(self.n_channels)]

        channel_names = [self.channel_labels[i] for i in order]
        channel_fluors = [self.channel_names[i] for i in order]

        data = np.array(self.get_image_stack_cyx(order), dtype=np.float32)
        to_tiff(
            data,
            filename,
            ome_channel_xml_fun=get_ome_channel_xml,
            channel_names=channel_names,
            channel_fluors=channel_fluors,
        )
