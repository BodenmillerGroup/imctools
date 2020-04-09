from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Dict, Optional

import imctools.io.mcd.constants as const

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict


if TYPE_CHECKING:
    from imctools.data.acquisition import Acquisition
    from imctools.data.panorama import Panorama
    from imctools.data.session import Session


class SlideDict(TypedDict):
    session_id: str
    id: int
    description: Optional[str]
    width_um: Optional[int]
    height_um: Optional[int]
    has_slide_image: Optional[bool]
    metadata: Optional[Dict[str, str]]


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
        has_slide_image: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
    ):
        """
        Parameters
        ----------
        session_id
            Parent session id (UUID).
        id
            Original slide ID.
        description
            Description.
        width_um
            Slide width (in μm).
        height_um
            Slide height (in μm).
        has_slide_image
            Whether a slide image exists.
        metadata
            Original (raw) metadata as a dictionary.
        """
        self.session_id = session_id
        self.id = id
        self.description = description
        self.width_um = width_um
        self.height_um = height_um
        self.has_slide_image = has_slide_image
        self.metadata = metadata if metadata is not None else dict()

        self.session: Optional[Session] = None  # Parent session object
        self.acquisitions: Dict[int, Acquisition] = dict()  # Children acquisitions
        self.panoramas: Dict[int, Panorama] = dict()  # Children panoramas

    @staticmethod
    def from_dict(d: SlideDict):
        """Recreate an object from dictionary"""
        result = Slide(
            d.get("session_id"),
            d.get("id"),
            description=d.get("description"),
            width_um=d.get("width_um"),
            height_um=d.get("height_um"),
            has_slide_image=d.get("has_slide_image"),
            metadata=d.get("metadata"),
        )
        return result

    @property
    def metaname(self):
        """Meta name fully describing the entity"""
        parent_name = self.session.metaname
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

    def get_csv_dict(self):
        """Returns dictionary for CSV tables"""
        s = self.__getstate__()
        del s["metadata"]
        return s

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, description={self.description})"
