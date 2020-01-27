from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional

from yaml import YAMLObject

if TYPE_CHECKING:
    from imctools.data.acquisition import Acquisition
    from imctools.data.panorama import Panorama
    from imctools.data.session import Session


class Slide(YAMLObject):
    """IMC slide
    """

    yaml_tag = "!Slide"
    symbol = "s"

    def __init__(
        self,
        session_id: str,
        id: int,
        description: Optional[str] = None,
        width_um: Optional[int] = None,
        height_um: Optional[int] = None,
        metadata: Dict[str, str] = None,
    ):
        self.session_id = session_id
        self.id = id
        self.description = description
        self.width_um = width_um
        self.height_um = height_um
        self.metadata = metadata

        self.session: Optional[Session] = None
        self.acquisitions: Dict[int, Acquisition] = dict()
        self.panoramas: Dict[int, Panorama] = dict()

    @property
    def meta_name(self):
        parent_name = self.session.meta_name
        return f"{parent_name}_{self.symbol}{self.id}"

    def __getstate__(self):
        """Returns dictionary for JSON/YAML serialization"""
        s = self.__dict__.copy()
        del s["session"]
        del s["acquisitions"]
        del s["panoramas"]
        return s

    def __repr__(self):
            return f"{self.__class__.__name__}(id={self.id}, description={self.description})"
