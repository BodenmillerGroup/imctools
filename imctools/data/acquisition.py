import logging
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Sequence, Any

import numpy as np
from dateutil.parser import parse
from xtiff import to_tiff

from imctools import __version__
from imctools.data.channel import Channel
from imctools.data.slide import Slide
from imctools.io.errors import AcquisitionError
from imctools.io.utils import get_ome_xml

logger = logging.getLogger(__name__)


class AblationImageType(Enum):
    BEFORE = "before"
    AFTER = "after"


class Acquisition:
    """IMC acquisition as a collection of acquisition channels."""

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
        before_ablation_image_exists: bool = False,
        after_ablation_image_exists: bool = False,
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
        self.metadata = metadata if metadata is not None else dict()
        self.before_ablation_image_exists = before_ablation_image_exists
        self.after_ablation_image_exists = after_ablation_image_exists

        self.slide: Optional[Slide] = None
        self.channels: Dict[int, Channel] = dict()

        self._image_data: Optional[np.ndarray] = None

    @staticmethod
    def from_dict(d: Dict[str, Any]):
        """Recreate an object from dictionary"""
        result = Acquisition(
            int(d.get("slide_id")),
            int(d.get("id")),
            int(d.get("max_x")),
            int(d.get("max_y")),
            d.get("signal_type"),
            d.get("segment_data_format"),
            float(d.get("ablation_frequency")),
            float(d.get("ablation_power")),
            parse(d.get("start_timestamp")),
            parse(d.get("end_timestamp")),
            d.get("movement_type"),
            float(d.get("ablation_distance_between_shots_x")),
            float(d.get("ablation_distance_between_shots_y")),
            d.get("template"),
            float(d.get("roi_start_x_pos_um")),
            float(d.get("roi_start_y_pos_um")),
            float(d.get("roi_end_x_pos_um")),
            float(d.get("roi_end_y_pos_um")),
            d.get("description"),
            d.get("metadata"),
            bool(d.get("before_ablation_image_exists")),
            bool(d.get("after_ablation_image_exists")),
        )
        return result

    @property
    def meta_name(self):
        """Meta name fully describing the entity"""
        parent_name = self.slide.meta_name
        return f"{parent_name}_{self.symbol}{self.id}"

    @property
    def image_data(self):
        return self._image_data

    @image_data.setter
    def image_data(self, value: Optional[np.ndarray]):
        self._image_data = value

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
        if self.image_data is None:
            raise AcquisitionError(f"Image data missing in acquisition {self.meta_name}")
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

    def save_ome_tiff(
        self,
        filename: str,
        names: Sequence[str] = None,
        masses: Sequence[str] = None,
        xml_metadata: Optional[str] = None,
    ):
        """Save OME TIFF file"""

        if self.image_data is None:
            return

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
            acquisition_date=self.start_timestamp.isoformat() if self.start_timestamp else None,
            image_date=self.start_timestamp,
            xml_metadata=xml_metadata,
        )

    def __getstate__(self):
        """Returns dictionary for JSON/YAML serialization"""
        s = self.__dict__.copy()
        s["start_timestamp"] = s["start_timestamp"].isoformat() if s["start_timestamp"] is not None else None
        s["end_timestamp"] = s["end_timestamp"].isoformat() if s["end_timestamp"] is not None else None
        del s["slide"]
        del s["channels"]
        del s["image_data"]
        return s

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, description={self.description})"
