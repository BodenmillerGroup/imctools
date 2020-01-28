from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional

from yaml import YAMLObject

if TYPE_CHECKING:
    from imctools.data.acquisition import Acquisition


class Channel(YAMLObject):
    """IMC acquisition channel. Represents an image intensity."""

    yaml_tag = "!Channel"
    symbol = "c"

    def __init__(
        self,
        acquisition_id: int,
        id: int,
        order_number: int,
        name: str,
        label: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        min_intensity: Optional[float] = None,
        max_intensity: Optional[float] = None,
    ):
        """
        Parameters
        ----------
        acquisition_id
            Parent acquisition ID
        id
            Original channel ID
        order_number
            Channel order number in acquisition
        name
            Channel name (unique per acquisition)
        label
            Channel label
        metadata
            Original (raw) channel metadata
        min_intensity
            Minimal intensity value
        max_intensity
            Maximum intensity value
        """
        self.acquisition_id = acquisition_id
        self.id = id
        self.order_number = order_number
        self.name = name
        self.label = label
        self.metadata = metadata
        self.min_intensity = min_intensity
        self.max_intensity = max_intensity

        self.acquisition: Optional[Acquisition] = None  # Parent acquisition

    @property
    def meta_name(self):
        """Meta name fully describing the entity"""
        parent_name = self.acquisition.meta_name
        return f"{parent_name}_{self.symbol}{self.id}"

    def get_image(self):
        """Get raster channel image"""
        return self.acquisition.get_image_by_name(self.name)

    def __getstate__(self):
        """Returns dictionary for JSON/YAML serialization"""
        s = self.__dict__.copy()
        del s["acquisition"]
        return s

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name}, label={self.label})"
