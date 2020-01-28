from datetime import datetime
from typing import Dict, Optional, Sequence

import numpy as np
from xtiff import to_tiff
from yaml import YAMLObject

from imctools import __version__
from imctools.data.channel import Channel
from imctools.data.slide import Slide
from imctools.io.utils import get_ome_xml


class Acquisition(YAMLObject):
    """IMC acquisition as a collection of acquisition channels."""

    yaml_tag = "!Acquisition"
    symbol = "a"

    def __init__(
        self,
        slide_id: int,
        id: int,
        max_x: int,
        max_y: int,
        signal_type: Optional[str] = None,
        segment_data_format: Optional[str] = None,
        ablation_frequency: Optional[float] = None,
        ablation_power: Optional[float] = None,
        start_timestamp: Optional[datetime] = None,
        end_timestamp: Optional[datetime] = None,
        movement_type: Optional[str] = None,
        ablation_distance_between_shots_x: Optional[float] = None,
        ablation_distance_between_shots_y: Optional[float] = None,
        template: Optional[str] = None,
        roi_start_x_pos_um: Optional[float] = None,
        roi_start_y_pos_um: Optional[float] = None,
        roi_end_x_pos_um: Optional[float] = None,
        roi_end_y_pos_um: Optional[float] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ):
        """
        Parameters
        ----------
        slide_id
            Parent slide ID
        id
            Original acquisition ID
        max_x
            Acquisition width in pixels
        max_y
            Acquisition height in pixels
        signal_type
            Signal type (Dual, etc)
        segment_data_format
            Data format (Float, etc)
        ablation_frequency
            Ablation frequency
        ablation_power
            Ablation power
        start_timestamp
            Acquisition start timestamp
        end_timestamp
            Acquisition end timestamp
        movement_type
            Movement type (XRaster, YRaster, etc)
        ablation_distance_between_shots_x
            Horizontal ablation distance between shots (in μm)
        ablation_distance_between_shots_y
            Vertical ablation distance between shots (in μm)
        template
            Template name
        roi_start_x_pos_um
            Start X position on the slide (in μm)
        roi_start_y_pos_um
            Start Y position on the slide (in μm)
        roi_end_x_pos_um
            End X position on the slide (in μm)
        roi_end_y_pos_um
            End Y position on the slide (in μm)
        description
            Acquisition description
        metadata
            Original (raw) metadata as a dictionary
        """
        self.slide_id = slide_id
        self.id = id
        self.max_x = max_x
        self.max_y = max_y
        self.signal_type = signal_type
        self.segment_data_format = segment_data_format
        self.ablation_frequency = ablation_frequency
        self.ablation_power = ablation_power
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.movement_type = movement_type
        self.ablation_distance_between_shots_x = ablation_distance_between_shots_x
        self.ablation_distance_between_shots_y = ablation_distance_between_shots_y
        self.template = template
        self.roi_start_x_pos_um = roi_start_x_pos_um
        self.roi_start_y_pos_um = roi_start_y_pos_um
        self.roi_end_x_pos_um = roi_end_x_pos_um
        self.roi_end_y_pos_um = roi_end_y_pos_um
        self.description = description
        self.metadata = metadata

        self.slide: Optional[Slide] = None
        self.channels: Dict[int, Channel] = dict()

        self.image_data: Optional[np.ndarray] = None

    @property
    def meta_name(self):
        """Meta name fully describing the entity"""
        parent_name = self.slide.meta_name
        return f"{parent_name}_{self.symbol}{self.id}"

    @property
    def n_channels(self):
        """Number of channels"""
        return len(self.channels)

    @property
    def channel_names(self):
        """Channel names"""
        channel_names = [c.name for c in self.channels.values()]
        return channel_names

    @property
    def channel_labels(self):
        """Channel labels"""
        channel_labels = [c.label for c in self.channels.values()]
        return channel_labels

    @property
    def channel_masses(self):
        """Channel masses"""
        return ["".join([n for n in name if n.isdigit()]) for name in self.channel_names]

    def get_name_indices(self, names: Sequence[str]):
        """Returns a list with the indices from names"""
        order_dict = dict()
        for i, v in enumerate(self.channel_names):
            order_dict.update({v: i})
        return [order_dict[n] for n in names]

    def get_mass_indices(self, masses: Sequence[str]):
        """Returns the channel indices from the queried mass"""
        order_dict = dict()
        for i, v in enumerate(self.channel_masses):
            order_dict.update({v: i})
        return [order_dict[m] for m in masses]

    def _get_image_stack_cyx(self, indices: Sequence[int] = None) -> Sequence[np.ndarray]:
        """Return the data reshaped as a stack of images"""
        if indices is None:
            indices = range(self.n_channels)
        img = [self.image_data[i] for i in indices]
        return img

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

    def save_ome_tiff(self, filename: str, names: Sequence[str] = None, masses: Sequence[str] = None):
        """Save OME TIFF file"""
        if names is not None:
            order = self.get_name_indices(names)
        elif masses is not None:
            order = self.get_mass_indices(masses)
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
            image_date=self.start_timestamp,
        )

    def __getstate__(self):
        """Returns dictionary for JSON/YAML serialization"""
        s = self.__dict__.copy()
        del s["slide"]
        del s["channels"]
        del s["image_data"]
        return s

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, description={self.description})"
