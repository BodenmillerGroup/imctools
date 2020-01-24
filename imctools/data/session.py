from __future__ import annotations

import json
from typing import Any, Dict, Optional

from imctools.data.ablation_image import AblationImage
from imctools.data.acquisition import Acquisition
from imctools.data.channel import Channel
from imctools.data.panorama import Panorama
from imctools.data.slide import Slide


class Session:
    """IMC session data

    """

    def __init__(
        self,
        id: str,
        name: str,
        software_version: str,
        origin: str,
        source_path: str,
        created: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.id = id
        self.name = name
        self.software_version = software_version
        self.origin = origin
        self.source_path = source_path
        self.created = created
        self.metadata = metadata

        self.slides: Dict[int, Slide] = dict()
        self.acquisitions: Dict[int, Acquisition] = dict()
        self.panoramas: Dict[int, Panorama] = dict()
        self.channels: Dict[int, Channel] = dict()
        self.ablation_images: Dict[int, AblationImage] = dict()

    def to_dict(self):
        """Returns dictionary for JSON/YAML serialization"""
        d = self.__dict__.copy()
        return d

    def save(self, filepath: str):
        """Save session data in JSON format

        Parameters
        ----------
        filepath
            output file path

        """

        def handle_default(obj):
            if isinstance(obj, (Session, Slide, Panorama, Acquisition, AblationImage, Channel)):
                return obj.to_dict()
            return None

        with open(filepath, "w") as f:
            json.dump(self, f, indent=2, default=handle_default)

    @staticmethod
    def load(filepath: str):
        with open(filepath, "r") as f:
            d = json.load(f)
        session = Session(d.get("id"), d.get("name"), d.get("software_version"), d.get("origin"), d.get("source_path"), d.get("created"), d.get("metadata"))
        return session

    @property
    def meta_name(self):
        return self.name

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()
    session = Session.load("/home/anton/Downloads/IMMUcan_Batch20191023_10032401-HN-VAR-TIS-01-IMC-01_AC2.json")
    print(timeit.default_timer() - tic)
