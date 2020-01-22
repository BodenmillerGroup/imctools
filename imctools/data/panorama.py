from __future__ import annotations

from typing import Dict, Optional

from imctools.data.slide import Slide


class Panorama:
    """Panoramic image and its description

    """

    symbol = "p"

    def __init__(
        self,
        slide_id: str,
        original_id: str,
        image_type: str,
        description: str,
        start_position_x: float,
        start_position_y: float,
        width: float,
        height: float,
        rotation_angle: float,
        file_extension: Optional[str] = None,
        meta: Optional[Dict[str, str]] = None,
    ):
        self.slide_id = slide_id
        self.original_id = original_id
        self.image_type = image_type
        self.description = description
        self.start_position_x = start_position_x
        self.start_position_y = start_position_y
        self.width = width
        self.height = height
        self.rotation_angle = rotation_angle
        self.file_extension = file_extension
        self.meta = meta

        self.slide: Optional[Slide] = None

    @property
    def meta_name(self):
        parent_name = self.slide.meta_name
        return f"{parent_name}_{self.symbol}_{self.original_id}"

    def to_dict(self):
        """Returns dictionary for JSON/YAML serialization"""
        d = self.__dict__.copy()
        d.pop("slide")
        return d

    def __repr__(self):
        return f"{self.__class__.__name__}(original_id={self.original_id}, image_type={self.image_type}, description={self.description})"
