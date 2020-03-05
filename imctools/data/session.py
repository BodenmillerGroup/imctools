from __future__ import annotations

import csv
import os
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import json

from dateutil.parser import parse

from imctools.data.acquisition import Acquisition
from imctools.data.channel import Channel
from imctools.data.panorama import Panorama
from imctools.data.slide import Slide
from imctools.io.utils import META_CSV_SUFFIX


class Session:
    """IMC session data. Container for all slides, acquisitions, panoramas, etc."""

    def __init__(
        self, id: str, name: str, imctools_version: str, created: datetime, metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Parameters
        ----------
        id
            Unique ID of the session (UUID)
        name
            Session name
        imctools_version
            Version of imctools library used for conversion
        created
            Datetime of session creation
        metadata
            Whole set of original (raw) metadata as a dictionary
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
    def from_dict(d: Dict[str, Any]):
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
        """Save session data in JSON format

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

    def save_meta_csv(self, output_folder: str):
        """Writes the metadata as CSV tables"""
        if not (os.path.exists(output_folder)):
            os.makedirs(output_folder)
        Session._save_csv(
            os.path.join(output_folder, "_".join([self.meta_name, "session"]) + META_CSV_SUFFIX), [self.get_csv_dict()]
        )
        Session._save_csv(
            os.path.join(output_folder, "_".join([self.meta_name, "slides"]) + META_CSV_SUFFIX),
            [v.get_csv_dict() for v in self.slides.values()],
        )
        Session._save_csv(
            os.path.join(output_folder, "_".join([self.meta_name, "panoramas"]) + META_CSV_SUFFIX),
            [v.get_csv_dict() for v in self.panoramas.values()],
        )
        Session._save_csv(
            os.path.join(output_folder, "_".join([self.meta_name, "acquisitions"]) + META_CSV_SUFFIX),
            [v.get_csv_dict() for v in self.acquisitions.values()],
        )
        Session._save_csv(
            os.path.join(output_folder, "_".join([self.meta_name, "channels"]) + META_CSV_SUFFIX),
            [v.get_csv_dict() for v in self.channels.values()],
        )

    @staticmethod
    def _save_csv(filepath: str, values: list):
        with open(filepath, "wt") as f:
            cols = values[0].keys()
            writer = csv.DictWriter(f, sorted(cols))
            writer.writeheader()
            writer.writerows(values)

    @staticmethod
    def load(filepath: str):
        """Load IMC session data from JSON file

        Parameters
        ----------
        filepath
            Input JSON file path
        """
        with open(filepath, "r") as f:
            data = json.load(f)
            return Session._rebuild_object_tree(data)

    @staticmethod
    def _rebuild_object_tree(data: Dict[str, Any]):
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

        return session

    @property
    def meta_name(self):
        """Meta name fully describing the entity"""
        return self.name

    @property
    def acquisition_indices(self) -> Tuple[int, ...]:
        return tuple(self.acquisitions.keys())

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()
    session = Session.load(
        "/home/anton/Downloads/imc_from_mcd/IMMUcan_Batch20191023_10032401-HN-VAR-TIS-01-IMC-01_AC2.json"
    )
    print(timeit.default_timer() - tic)
