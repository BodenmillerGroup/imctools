import logging
import sys
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Sequence

from dateutil.parser import parse

from imctools.data.channel import Channel
from imctools.data.slide import Slide

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict


logger = logging.getLogger(__name__)


class AblationImageType(Enum):
    """Before / after ablation types of images"""

    BEFORE = "before"
    AFTER = "after"


class AcquisitionDict(TypedDict):
    slide_id: int
    id: int
    origin: str
    source_path: str
    max_x: int
    max_y: int
    signal_type: Optional[str]
    segment_data_format: Optional[str]
    ablation_frequency: Optional[float]
    ablation_power: Optional[float]
    start_timestamp: Optional[str]
    end_timestamp: Optional[str]
    movement_type: Optional[str]
    ablation_distance_between_shots_x: Optional[float]
    ablation_distance_between_shots_y: Optional[float]
    template: Optional[str]
    roi_start_x_pos_um: Optional[float]
    roi_start_y_pos_um: Optional[float]
    roi_end_x_pos_um: Optional[float]
    roi_end_y_pos_um: Optional[float]
    description: Optional[str]
    has_before_ablation_image: bool
    has_after_ablation_image: bool
    metadata: Optional[Dict[str, str]]
    is_valid: bool


class Acquisition:
    """IMC acquisition as a collection of acquisition channels."""

    symbol = "a"

    def __init__(
        self,
        slide_id: int,
        id: int,
        origin: str,
        source_path: str,
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
        has_before_ablation_image: bool = False,
        has_after_ablation_image: bool = False,
        metadata: Optional[Dict[str, str]] = None,
        is_valid: bool = True,
    ):
        """
        Parameters
        ----------
        slide_id
            Parent slide ID.
        id
            Original acquisition ID.
        origin
            Origin of the data (mcd, txt, etc).
        source_path
            Path to data source file.
        max_x
            Acquisition width in pixels.
        max_y
            Acquisition height in pixels.
        signal_type
            Signal type (Dual, etc).
        segment_data_format
            Data format (Float, etc).
        ablation_frequency
            Ablation frequency.
        ablation_power
            Ablation power.
        start_timestamp
            Acquisition start timestamp.
        end_timestamp
            Acquisition end timestamp.
        movement_type
            Movement type (XRaster, YRaster, etc).
        ablation_distance_between_shots_x
            Horizontal ablation distance between shots (in μm).
        ablation_distance_between_shots_y
            Vertical ablation distance between shots (in μm).
        template
            Template name.
        roi_start_x_pos_um
            Start X position on the slide (in μm).
        roi_start_y_pos_um
            Start Y position on the slide (in μm).
        roi_end_x_pos_um
            End X position on the slide (in μm).
        roi_end_y_pos_um
            End Y position on the slide (in μm).
        description
            Acquisition description.
        has_before_ablation_image
            Whether before ablation image exists.
        has_after_ablation_image
            Whether after ablation image exists.
        metadata
            Original (raw) metadata as a dictionary.
        """
        self.slide_id = slide_id
        self.id = id
        self.origin = origin
        self.source_path = source_path
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
        self.has_before_ablation_image = has_before_ablation_image
        self.has_after_ablation_image = has_after_ablation_image
        self.metadata = metadata if metadata is not None else dict()
        self.is_valid = is_valid

        self.slide: Optional[Slide] = None
        self.channels: Dict[int, Channel] = dict()

    @staticmethod
    def from_dict(d: AcquisitionDict):
        """Recreate an object from dictionary"""
        result = Acquisition(
            d.get("slide_id"),
            d.get("id"),
            d.get("origin"),
            d.get("source_path"),
            d.get("max_x"),
            d.get("max_y"),
            signal_type=d.get("signal_type"),
            segment_data_format=d.get("segment_data_format"),
            ablation_frequency=d.get("ablation_frequency"),
            ablation_power=d.get("ablation_power"),
            start_timestamp=parse(d.get("start_timestamp")),
            end_timestamp=parse(d.get("end_timestamp")),
            movement_type=d.get("movement_type"),
            ablation_distance_between_shots_x=d.get("ablation_distance_between_shots_x"),
            ablation_distance_between_shots_y=d.get("ablation_distance_between_shots_y"),
            template=d.get("template"),
            roi_start_x_pos_um=d.get("roi_start_x_pos_um"),
            roi_start_y_pos_um=d.get("roi_start_y_pos_um"),
            roi_end_x_pos_um=d.get("roi_end_x_pos_um"),
            roi_end_y_pos_um=d.get("roi_end_y_pos_um"),
            description=d.get("description"),
            has_before_ablation_image=d.get("has_before_ablation_image"),
            has_after_ablation_image=d.get("has_after_ablation_image"),
            metadata=d.get("metadata"),
            is_valid=d.get("is_valid"),
        )
        return result

    @property
    def metaname(self):
        """Meta name fully describing the entity"""
        parent_name = self.slide.metaname
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

    def __getstate__(self):
        """Returns dictionary for JSON/YAML serialization"""
        s = self.__dict__.copy()
        s["start_timestamp"] = s["start_timestamp"].isoformat() if s["start_timestamp"] is not None else None
        s["end_timestamp"] = s["end_timestamp"].isoformat() if s["end_timestamp"] is not None else None
        del s["slide"]
        del s["channels"]
        return s

    def get_csv_dict(self):
        """Returns dictionary for CSV tables"""
        s = self.__getstate__()
        del s["metadata"]
        return s

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, description={self.description})"
