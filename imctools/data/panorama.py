from __future__ import annotations

from typing import Dict, Optional, TypedDict

from imctools.data.slide import Slide


class PanoramaDict(TypedDict):
    slide_id: int
    id: int
    image_type: str
    description: str
    start_position_x: float
    start_position_y: float
    width: float
    height: float
    rotation_angle: float
    metadata: Optional[Dict[str, str]]


class Panorama:
    """Panoramic image (manually attached or automatically generated)."""

    symbol = "p"

    def __init__(
        self,
        slide_id: int,
        id: int,
        image_type: str,
        description: str,
        start_position_x: float,
        start_position_y: float,
        width: float,
        height: float,
        rotation_angle: float,
        metadata: Optional[Dict[str, str]] = None,
    ):
        """
        Parameters
        ----------
        slide_id
            Parent slide ID.
        id
            Original panorama ID.
        image_type
            Image type (Imported, Instrument, Default).
        description
            Panorama description.
        start_position_x
            X coordinate of start panorama position on the slide (in μm).
        start_position_y
            Y coordinate of start panorama position on the slide (in μm).
        width
            Panorama physical width (in μm).
        height
            Panorama physical height (in μm).
        rotation_angle
            Panorama rotation angle (degrees).
        metadata
            Original (raw) metadata as a dictionary.
        """
        self.slide_id = slide_id
        self.id = id
        self.image_type = image_type
        self.description = description
        self.start_position_x = start_position_x
        self.start_position_y = start_position_y
        self.width = width
        self.height = height
        self.rotation_angle = rotation_angle
        self.metadata = metadata

        self.slide: Optional[Slide] = None

    @staticmethod
    def from_dict(d: PanoramaDict):
        """Recreate an object from dictionary"""
        result = Panorama(
            d.get("slide_id"),
            d.get("id"),
            d.get("image_type"),
            d.get("description"),
            d.get("start_position_x"),
            d.get("start_position_y"),
            d.get("width"),
            d.get("height"),
            d.get("rotation_angle"),
            metadata=d.get("metadata"),
        )
        return result

    @property
    def meta_name(self):
        """Meta name fully describing the entity"""
        parent_name = self.slide.meta_name
        return f"{parent_name}_{self.symbol}{self.id}"

    def __getstate__(self):
        """Returns dictionary for JSON/YAML serialization"""
        s = self.__dict__.copy()
        del s["slide"]
        return s

    def get_csv_dict(self):
        """Returns dictionary for CSV tables"""
        s = self.__getstate__()
        del s["metadata"]
        return s

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, image_type={self.image_type}, description={self.description})"
