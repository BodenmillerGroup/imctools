from __future__ import annotations

from typing import Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from imctools.data.acquisition import Acquisition
    from imctools.data.panorama import Panorama
    from imctools.data.session import Session


class Slide:
    """IMC slide

    """

    def __init__(
        self,
        session_id: str,
        original_id: str,
        physical_width: Optional[float] = None,
        physical_height: Optional[float] = None,
        description: Optional[str] = None,
    ):
        self.session_id = session_id
        self.original_id = original_id
        self.physical_width = physical_width
        self.physical_height = physical_height
        self.description = description

    def __repr__(self):
        return f"{self.__class__.__name__}(original_id={self.original_id}, description={self.description})"
