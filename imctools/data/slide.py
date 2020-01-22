from __future__ import annotations

from typing import Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from imctools.data.acquisition import Acquisition
    from imctools.data.panorama import Panorama
    from imctools.data.session import Session


class Slide:
    """IMC slide

    """

    symbol = "s"

    def __init__(
        self,
        session_id: str,
        original_id: str,
        physical_width: Optional[float] = None,
        physical_height: Optional[float] = None,
        description: Optional[str] = None,
        meta: Dict[str, str] = None,
    ):
        self.session_id = session_id
        self.original_id = original_id
        self.physical_width = physical_width
        self.physical_height = physical_height
        self.description = description
        self.meta = meta

        self.session: Optional[Session] = None
        self.acquisitions: Dict[str, Acquisition] = dict()
        self.panoramas: Dict[str, Panorama] = dict()

    @property
    def meta_name(self):
        parent_name = self.session.meta_name
        return f"{parent_name}_{self.symbol}_{self.original_id}"

    def to_dict(self):
        """Returns dictionary for JSON/YAML serialization"""
        d = self.__dict__.copy()
        d.pop("session")
        d.pop("acquisitions")
        d.pop("panoramas")
        return d

    def __repr__(self):
        return f"{self.__class__.__name__}(original_id={self.original_id}, description={self.description})"
