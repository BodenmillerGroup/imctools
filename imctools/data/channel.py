from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Dict, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict

if TYPE_CHECKING:
    from imctools.data.acquisition import Acquisition


class ChannelDict(TypedDict):
    acquisition_id: int
    id: int
    order_number: int
    name: str
    label: Optional[str]
    mass: Optional[int]
    min_intensity: Optional[float]
    max_intensity: Optional[float]
    metadata: Optional[Dict[str, str]]


class Channel:
    """IMC acquisition channel. Represents an image intensity."""

    symbol = "c"

    def __init__(
        self,
        acquisition_id: int,
        id: int,
        order_number: int,
        name: str,
        label: Optional[str] = None,
        mass: Optional[int] = None,
        min_intensity: Optional[float] = None,
        max_intensity: Optional[float] = None,
        metadata: Optional[Dict[str, str]] = None,
    ):
        """
        Parameters
        ----------
        acquisition_id
            Parent acquisition ID.
        id
            Original channel ID.
        order_number
            Channel order number in acquisition.
        name
            Channel name (unique per acquisition).
        label
            Channel label.
        mass
            Channel atomic mass.
        min_intensity
            Minimal intensity value.
        max_intensity
            Maximum intensity value.
        metadata
            Original (raw) channel metadata.
        """
        self.acquisition_id = acquisition_id
        self.id = id
        self.order_number = order_number
        self.name = name
        self.label = label
        self.mass = mass
        self.min_intensity = min_intensity
        self.max_intensity = max_intensity
        self.metadata = metadata

        self.acquisition: Optional[Acquisition] = None  # Parent acquisition

    @staticmethod
    def from_dict(d: ChannelDict):
        """Recreate an object from dictionary"""
        result = Channel(
            d.get("acquisition_id"),
            d.get("id"),
            d.get("order_number"),
            d.get("name"),
            label=d.get("label"),
            mass=d.get("mass"),
            min_intensity=d.get("min_intensity") if d.get("min_intensity") is not None else None,
            max_intensity=d.get("max_intensity") if d.get("max_intensity") is not None else None,
            metadata=d.get("metadata"),
        )
        return result

    @property
    def metaname(self):
        """Meta name fully describing the entity"""
        parent_name = self.acquisition.metaname
        return f"{parent_name}_{self.symbol}{self.id}"

    def __getstate__(self):
        """Returns dictionary for JSON/YAML serialization"""
        s = self.__dict__.copy()
        del s["acquisition"]
        return s

    def get_csv_dict(self):
        """Returns dictionary for CSV tables"""
        s = self.__getstate__()
        del s["metadata"]
        return s

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name}, label={self.label})"
