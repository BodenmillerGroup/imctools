from datetime import datetime
from typing import Dict, List, Optional

from imctools.data.channel import Channel
from imctools.data.slide import Slide


class Acquisition:
    """Image acquisition

    """

    def __init__(
        self,
        slide_id: str,
        original_id: str,
        image_width: int,
        image_height: int,
        signal_type: str,
        is_valid: bool,
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
    ):
        self.slide_id = slide_id
        self.original_id = original_id
        self.image_width = image_width
        self.image_height = image_height
        self.signal_type = signal_type
        self.is_valid = is_valid
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

    @property
    def to_dict(self):
        return {
            "original_id": self.original_id,
            "acquisition_id": self.acquisition_id,
            "order_number": self.order_number,
            "name": self.name,
            "label": self.label,
            "min_intensity": self.min_intensity,
            "max_intensity": self.max_intensity,
        }

    def __repr__(self):
        return f"{self.__class__.__name__}(original_id={self.original_id}, description={self.description})"
