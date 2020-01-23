from datetime import datetime
from typing import Dict, Optional, Sequence

import numpy as np
from xtiff import to_tiff

from imctools.data.channel import Channel
from imctools.data.slide import Slide
from imctools.io.utils import get_ome_channel_xml


class Acquisition:
    """Image acquisition

    """

    symbol = "a"

    def __init__(
        self,
        slide_id: str,
        original_id: str,
        max_x: int,
        max_y: int,
        signal_type: str,
        data_format: str,
        ablation_freq: Optional[float] = None,
        ablation_power: Optional[float] = None,
        ablation_start_time: Optional[datetime] = None,
        ablation_end_time: Optional[datetime] = None,
        movement_type: Optional[str] = None,
        pixel_size_x: Optional[float] = None,
        pixel_size_y: Optional[float] = None,
        pixel_spacing_x: Optional[float] = None,
        pixel_spacing_y: Optional[float] = None,
        template: Optional[str] = None,
        start_x: Optional[float] = None,
        start_y: Optional[float] = None,
        end_x: Optional[float] = None,
        end_y: Optional[float] = None,
        description: Optional[str] = None,
        meta: Optional[Dict[str, str]] = None,
        offset: Optional[int] = 3,
    ):
        self.slide_id = slide_id
        self.original_id = original_id
        self.max_x = max_x
        self.max_y = max_y
        self.signal_type = signal_type
        self.data_format = data_format
        self.ablation_freq = ablation_freq
        self.ablation_power = ablation_power
        self.ablation_start_time = ablation_start_time
        self.ablation_end_time = ablation_end_time
        self.movement_type = movement_type
        self.pixel_size_x = pixel_size_x
        self.pixel_size_y = pixel_size_y
        self.pixel_spacing_x = pixel_spacing_x
        self.pixel_spacing_y = pixel_spacing_y
        self.template = template
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.description = description
        self.meta = meta
        self._offset = offset

        self.slide: Optional[Slide] = None
        self.channels: Optional[Dict[str, Channel]] = dict()
        self.image_data: Optional[np.ndarray] = None

    @property
    def meta_name(self):
        parent_name = self.slide.meta_name
        return f"{parent_name}_{self.symbol}_{self.original_id}"

    @property
    def n_channels(self):
        return len(self.channels) - self._offset

    @property
    def channel_names(self):
        """Channel names

        Offset is taken into account (in order to skip X, Y, Z channels)

        """
        channel_names = [c.name for c in self.channels.values()]
        return channel_names[self._offset :]

    @property
    def channel_labels(self):
        """Channel labels

        Offset is taken into account (in order to skip X, Y, Z channels)

        """
        channel_labels = [c.label for c in self.channels.values()]
        return channel_labels[self._offset :]

    @property
    def channel_masses(self):
        """Channel masses

        Offset is taken into account (in order to skip X, Y, Z channels)

        """
        return ["".join([n for n in name if n.isdigit()]) for name in self.channel_names]

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

    def _get_image_stack_cyx(self, indices: Sequence[int] = None, offset: int = None) -> Sequence[np.ndarray]:
        """Return the data reshaped as a stack of images

        """
        if offset is None:
            offset = self._offset

        if indices is None:
            indices = range(self.n_channels)

        img = [self.image_data[i + offset] for i in indices]
        return img

    def get_image_by_index(self, index: int):
        """Get channel image by its index

        """
        stack = self._get_image_stack_cyx(indices=[index])
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

    def save_ome_tiff(self, filename: str, names: Sequence[str] = None, masses: Sequence[str] = None):
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

        data = np.array(self._get_image_stack_cyx(order), dtype=np.float32)
        to_tiff(
            data,
            filename,
            ome_channel_xml_fun=get_ome_channel_xml,
            channel_names=channel_names,
            channel_fluors=channel_fluors,
        )

    def to_dict(self):
        """Returns dictionary for JSON/YAML serialization"""
        d = self.__dict__.copy()
        d.pop("slide")
        d.pop("channels")
        d.pop("image_data")
        d.pop("_offset")
        return d

    def __repr__(self):
        return f"{self.__class__.__name__}(original_id={self.original_id}, description={self.description})"
