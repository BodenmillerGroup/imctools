from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Any

import imctools.io.mcd.constants as const
if TYPE_CHECKING:
    from imctools.data.acquisition import Acquisition
    from imctools.data.panorama import Panorama
    from imctools.data.session import Session


class Slide:
    """IMC slide (container for IMC acquisitions, panoramas and other entities)."""

    symbol = "s"

    def __init__(
        self,
        session_id: str,
        id: int,
        description: Optional[str] = None,
        width_um: Optional[int] = None,
        height_um: Optional[int] = None,
        metadata: Optional[Dict[str, str]] = None,
    ):
        """
        Parameters
        ----------
        session_id
            Parent session id (UUID)
        id
            Original slide ID
        description
            Description
        width_um
            Slide width (in μm)
        height_um
            Slide height (in μm)
        metadata
            Original (raw) metadata as a dictionary
        """
        self.session_id = session_id
        self.id = id
        self.description = description
        self.width_um = width_um
        self.height_um = height_um
        self.metadata = metadata

        self.session: Optional[Session] = None  # Parent session object
        self.acquisitions: Dict[int, Acquisition] = dict()  # Children acquisitions
        self.panoramas: Dict[int, Panorama] = dict()  # Children panoramas

    @staticmethod
    def from_dict(d: Dict[str, Any]):
        """Recreate an object from dictionary"""
        result = Slide(
            d.get("session_id"),
            int(d.get("id")),
            d.get("description"),
            int(d.get("width_um")),
            int(d.get("height_um")),
            d.get("metadata")
        )
        return result

    @property
    def meta_name(self):
        """Meta name fully describing the entity"""
        parent_name = self.session.meta_name
        return f"{parent_name}_{self.symbol}{self.id}"

    @property
    def name(self):
        """Slide name (if available)"""
        return self.metadata.get(const.NAME, None)

    @property
    def uid(self):
        """Slide UUID (if available)"""
        return self.metadata.get(const.UID, None)

    @property
    def filename(self):
        """Slide original source filename (if available)"""
        return self.metadata.get(const.FILENAME, None)

    @property
    def sw_version(self):
        """CyTOF software version (if available)"""
        return self.metadata.get(const.SW_VERSION, None)

    def __getstate__(self):
        """Returns dictionary for JSON/YAML serialization"""
        s = self.__dict__.copy()
        del s["session"]
        del s["acquisitions"]
        del s["panoramas"]
        return s

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, description={self.description})"
