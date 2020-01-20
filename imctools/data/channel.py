from __future__ import annotations

from typing import Dict, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from imctools.data.acquisition import Acquisition


class Channel:
    """
    IMC acquisition channel

    """

    def __init__(
        self,
        acquisition_id: str,
        original_id: str,
        name: str,
        label: Optional[str] = None,
        meta: Optional[Dict[str, str]] = None,
        min_intensity: Optional[float] = None,
        max_intensity: Optional[float] = None,
    ):
        self.acquisition_id = acquisition_id
        self.original_id = original_id
        self.name = name
        self.label = label
        self.meta = meta
        self.min_intensity = min_intensity
        self.max_intensity = max_intensity

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(original_id={self.original_id}, name={self.name}, label={self.label})"
        )
