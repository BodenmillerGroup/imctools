from __future__ import annotations

from typing import Sequence, Dict

import numpy as np
from xtiff import to_tiff

from imctools.data.ablation_image import AblationImageType, AblationImage
from imctools.data.channel import Channel
from imctools.io.utils import get_ome_channel_xml


class Acquisition:
    """General IMC acquisition class

    """
    def __init__(
        self,
        slide_id: str,
        original_id: str,
        data: np.ndarray,
        channel_names: Sequence[str],
        channel_labels: Sequence[str],
        meta: Dict[str, str] = None,
        origin: str = None,
        offset: int = 3,
    ):
        self.slide_id = slide_id
        self.original_id = original_id
        self._data = data
        self._channel_names = channel_names
        self._channel_labels = channel_labels
        self._meta = meta
        self._origin = origin
        self._offset = offset

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
        return self._channel_names[self._offset:]

    @property
    def channel_labels(self):
        """Channel labels

        Offset is taken into account (in order to skip X, Y, Z channels)

        """
        return self._channel_labels[self._offset:] if self._channel_labels is not None else None

    @property
    def channel_masses(self):
        """Channel masses

        Offset is taken into account (in order to skip X, Y, Z channels)

        """
        return ["".join([m for m in metal if m.isdigit()]) for metal in self.channel_names]

    def get_name_indices(self, names: Sequence[str]):
        """
        Returns a list with the indices from metals

        :param metals: List of metal names
        """
        order_dict = dict()
        for i, v in enumerate(self.channel_names):
            order_dict.update({v: i})

        return [order_dict[n] for n in names]

    def get_mass_indices(self, masses: Sequence[str]):
        """
        Returns the channel indices from the queried mass

        :param masses: List of metal masses
        """

        order_dict = dict()
        for i, v in enumerate(self.channel_masses):
            order_dict.update({v: i})

        return [order_dict[m] for m in masses]

    def get_image_stack_cyx(self, indices: Sequence[int] = None, offset: int = None):
        """Returns data reshaped as a stack of images

        """
        if offset is None:
            offset = self._offset

        if indices is None:
            indices = range(self.n_channels)

        img = [self._data[i + offset] for i in indices]
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

    def save_image(self, filename: str, names=None, mass=None):
        if names is not None:
            order = self.get_name_indices(names)
        elif mass is not None:
            order = self.get_mass_indices(mass)
        else:
            order = [i for i in range(self.n_channels)]

        channel_labels = [self.channel_labels[i] for i in order]
        channel_fluors = [self.channel_names[i] for i in order]

        data = np.array(self.get_image_stack_cyx(order), dtype=np.float32)
        to_tiff(
            data,
            filename,
            ome_channel_xml_fun=get_ome_channel_xml,
            channel_names=channel_labels,
            channel_fluors=channel_fluors,
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(original_id={self.original_id})"
