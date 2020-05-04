from __future__ import annotations

import sys
from typing import Dict, Optional

from imctools.data.slide import Slide

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict


class PanoramaDict(TypedDict):
    slide_id: int
    id: int
    image_type: str
    description: str
    x1: float
    y1: float
    x2: float
    y2: float
    x3: float
    y3: float
    x4: float
    y4: float
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
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        x3: float,
        y3: float,
        x4: float,
        y4: float,
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
        x1
            X1 coordinate of panorama position on the slide (in μm).
        y1
            Y1 coordinate of panorama position on the slide (in μm).
        x2
            X2 coordinate of panorama position on the slide (in μm).
        y2
            Y2 coordinate of panorama position on the slide (in μm).
        x3
            X3 coordinate of panorama position on the slide (in μm).
        y3
            Y3 coordinate of panorama position on the slide (in μm).
        x4
            X4 coordinate of panorama position on the slide (in μm).
        y4
            Y4 coordinate of panorama position on the slide (in μm).
        rotation_angle
            Panorama rotation angle (degrees).
        metadata
            Original (raw) metadata as a dictionary.
        """
        self.slide_id = slide_id
        self.id = id
        self.image_type = image_type
        self.description = description
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3
        self.x4 = x4
        self.y4 = y4
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
            d.get("x1"),
            d.get("y1"),
            d.get("x2"),
            d.get("y2"),
            d.get("x3"),
            d.get("y3"),
            d.get("x4"),
            d.get("y4"),
            d.get("rotation_angle"),
            metadata=d.get("metadata"),
        )
        return result

    @property
    def metaname(self):
        """Meta name fully describing the entity"""
        parent_name = self.slide.metaname
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
