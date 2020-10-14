from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from dateutil.parser import parse

from imctools.data.acquisition import Acquisition, AcquisitionDict
from imctools.data.channel import Channel, ChannelDict
from imctools.data.panorama import Panorama, PanoramaDict
from imctools.data.slide import Slide, SlideDict
from imctools.io.utils import META_CSV_SUFFIX, sort_acquisition_channels

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict


class SessionDict(TypedDict):
    id: str
    name: str
    imctools_version: str
    created: str
    metadata: Optional[Dict[str, Any]]
    slides: List[SlideDict]
    acquisitions: List[AcquisitionDict]
    panoramas: List[PanoramaDict]
    channels: List[ChannelDict]


class Session:
    """IMC session data. Container for all slides, acquisitions, panoramas, etc."""

    def __init__(
        self, id: str, name: str, imctools_version: str, created: datetime, metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Parameters
        ----------
        id
            Unique ID of the session (UUID).
        name
            Session name.
        imctools_version
            Version of imctools library used for conversion.
        created
            Datetime of session creation.
        metadata
            Whole set of original (raw) metadata as a dictionary.
        """
        self.id = id
        self.name = name
        self.imctools_version = imctools_version
        self.created = created
        self.metadata = metadata

        self.slides: Dict[int, Slide] = dict()
        self.acquisitions: Dict[int, Acquisition] = dict()
        self.panoramas: Dict[int, Panorama] = dict()
        self.channels: Dict[int, Channel] = dict()

    @staticmethod
    def from_dict(d: SessionDict):
        """Recreate an object from dictionary"""
        result = Session(
            d.get("id"), d.get("name"), d.get("imctools_version"), parse(d.get("created")), d.get("metadata"),
        )
        return result

    def __getstate__(self):
        """Returns dictionary for JSON/YAML serialization"""
        s = self.__dict__.copy()
        s["created"] = s["created"].isoformat()
        s["slides"] = list(s["slides"].values())
        s["acquisitions"] = list(s["acquisitions"].values())
        s["panoramas"] = list(s["panoramas"].values())
        s["channels"] = list(s["channels"].values())
        return s

    def get_csv_dict(self):
        """Returns dictionary for CSV tables"""
        s = self.__dict__.copy()
        s["created"] = s["created"].isoformat()
        del s["slides"]
        del s["acquisitions"]
        del s["panoramas"]
        del s["channels"]
        del s["metadata"]
        return s

    def save(self, filepath: str):
        """Save session data in JSON format.

        Parameters
        ----------
        filepath
            Output JSON file path
        """

        def handle_default(obj):
            if isinstance(obj, (Session, Slide, Panorama, Acquisition, Channel)):
                return obj.__getstate__()
            return None

        with open(filepath, "wt") as f:
            json.dump(self, f, indent=2, default=handle_default)

    def save_meta_csv(self, output_folder: Union[str, Path]):
        """Writes the metadata as CSV tables"""
        if isinstance(output_folder, str):
            output_folder = Path(output_folder)
        if not output_folder.exists():
            output_folder.mkdir(parents=True, exist_ok=True)
        Session._save_csv(
            output_folder / ("_".join([self.metaname, "session"]) + META_CSV_SUFFIX), [self.get_csv_dict()]
        )
        Session._save_csv(
            output_folder / ("_".join([self.metaname, "slides"]) + META_CSV_SUFFIX),
            [v.get_csv_dict() for v in self.slides.values()],
        )
        Session._save_csv(
            output_folder / ("_".join([self.metaname, "panoramas"]) + META_CSV_SUFFIX),
            [v.get_csv_dict() for v in self.panoramas.values()],
        )
        Session._save_csv(
            output_folder / ("_".join([self.metaname, "acquisitions"]) + META_CSV_SUFFIX),
            [v.get_csv_dict() for v in self.acquisitions.values()],
        )
        Session._save_csv(
            output_folder / ("_".join([self.metaname, "channels"]) + META_CSV_SUFFIX),
            [v.get_csv_dict() for v in self.channels.values()],
        )

    @staticmethod
    def _save_csv(filepath: Path, values: list):
        with open(filepath, "wt") as f:
            cols = values[0].keys()
            writer = csv.DictWriter(f, sorted(cols))
            writer.writeheader()
            writer.writerows(values)

    @staticmethod
    def load(filepath: Union[str, Path]):
        """Load IMC session data from JSON file

        Parameters
        ----------
        filepath
            Input JSON file path.
        """
        with open(filepath, "r") as f:
            data = json.load(f)
            return Session._rebuild_object_tree(data)

    @staticmethod
    def _rebuild_object_tree(data: SessionDict):
        """Helper function that re-creates parents/children relations between entities"""

        session = Session.from_dict(data)

        for item in data.get("slides"):
            slide = Slide.from_dict(item)
            slide.session = session
            session.slides[slide.id] = slide

        for item in data.get("panoramas"):
            panorama = Panorama.from_dict(item)
            slide = session.slides.get(panorama.slide_id)
            panorama.slide = slide
            slide.panoramas[panorama.id] = panorama
            session.panoramas[panorama.id] = panorama

        for item in data.get("acquisitions"):
            acquisition = Acquisition.from_dict(item)
            slide = session.slides.get(acquisition.slide_id)
            acquisition.slide = slide
            slide.acquisitions[acquisition.id] = acquisition
            session.acquisitions[acquisition.id] = acquisition

        for item in data.get("channels"):
            channel = Channel.from_dict(item)
            acquisition = session.acquisitions.get(channel.acquisition_id)
            channel.acquisition = acquisition
            acquisition.channels[channel.id] = channel
            session.channels[channel.id] = channel

        # Sort acquisitions channels by ORDER_NUMBER
        sort_acquisition_channels(session)

        return session

    @property
    def metaname(self):
        """Meta name fully describing the entity"""
        return self.name

    @property
    def acquisition_ids(self) -> Tuple[int, ...]:
        return tuple(self.acquisitions.keys())

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()
    session = Session.load(
        "/home/anton/Downloads/imc_folder_v2/20170905_Fluidigmworkshopfinal_SEAJa/20170905_Fluidigmworkshopfinal_SEAJa_session.json"
    )
    print(timeit.default_timer() - tic)
