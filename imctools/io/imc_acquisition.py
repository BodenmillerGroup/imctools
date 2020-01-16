from pathlib import Path
from typing import List

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
        channel_names,
        channel_labels,
        metadata=None,
        description: str = None,
        origin: str = None,
        offset: int = 0,
    ):
        """

        Parameters
        ----------
        original_id
            The acquisition ID
        filepath
            The original file path
        data
            Image data
        channel_names
            the channel (metal) names
        channel_labels
            the channel label (meaningful label)
        metadata
            the original metadata, e.g. an MCDPublic XML
        description
            the image description. For MCD acquisitions this is the metadata based name.
        """
        self.original_id = original_id
        self.filepath = filepath

        self._data = data
        self._offset = offset

        self._channel_names = self._validate_values(channel_names)
        self._channel_labels = self._validate_values(channel_labels)
        self.metadata = metadata
        self.description = description
        self.origin = origin

    @property
    def filename(self):
        return Path(self.filepath).name

    @property
    def n_channels(self):
        return len(self._data) - self._offset

    @property
    def shape(self):
        """
        Shape in cyx format
        """
        return self.data.shape

    @property
    def channel_names(self):
        return self._channel_names[self._offset :]

    @property
    def channel_masses(self):
        return ["".join([m for m in metal if m.isdigit()]) for metal in self._channel_names[self._offset :]]

    @property
    def channel_labels(self):
        return self._channel_labels[self._offset :] if self._channel_labels is not None else None

    def get_metal_indices(self, metals):
        """
        Returns a list with the indices from metals

        :param metals: List of metal names
        """
        order_dict = dict()
        for i, v in enumerate(self.channel_names):
            order_dict.update({v: i})

        return [order_dict[m] for m in metals]

    def get_mass_indices(self, masses):
        """
        Returns the channel indices from the queried mass

        :param masses: List of metal masses
        """

        order_dict = dict()
        for i, v in enumerate(self.channel_masses):
            order_dict.update({v: i})

        return [order_dict[m] for m in masses]

    @property
    def data(self):
        return self._data

    def get_image_stack_cyx(self, indices=None, offset=None):
        """
        Return the data reshaped as a stack of images

        :param: indices
        """
        if offset is None:
            offset = self._offset

        if indices is None:
            indices = range(self.n_channels)

        data = self._data
        img = [data[i + offset] for i in indices]
        return img

    def get_image_by_index(self, index: int):
        """

        :param index:
        """
        stack = self.get_image_stack_cyx(indices=[index])
        return stack[0]

    def get_image_by_name(self, name: str):
        index = self.channel_names.index(name)
        return self.get_image_by_index(index)

    def get_img_by_label(self, label: str):
        index = self.channel_labels.index(label)
        return self.get_image_by_index(index)

    def _validate_values(self, values: List[str]):
        if values is None:
            return None
        elif len(values) == self.n_channels:
            for i in range(self._offset):
                if i < 3:
                    values = ["X", "Y", "Z"][i] + values
                else:
                    values = [str(i)] + values
        elif len(values) == self.n_channels + self._offset:
            pass
        else:
            raise ValueError("Incompatible channel names/labels!")

        # remove special characters
        values = [v.replace("(", "").replace(")", "").strip() if v is not None else "" for v in values]
        return values

    def save_image(self, filename: str, metals=None, mass=None):
        if metals is not None:
            order = self.get_metal_indices(metals)
        elif mass is not None:
            order = self.get_mass_indices(mass)
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
