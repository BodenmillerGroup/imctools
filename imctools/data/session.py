from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from imctools.data.acquisition import Acquisition
from imctools.data.channel import Channel
from imctools.data.panorama import Panorama
from imctools.data.slide import Slide

import yaml


class Session:
    """IMC session data

    """

    def __init__(
        self, name: str, software_version: str, origin: str, origin_filepath: str,
    ):
        self.id = "0"
        self.name = name
        self.software_version = software_version
        self.origin = origin
        self.origin_filepath = origin_filepath

        self.slides: Dict[str, Slide] = dict()
        self.acquisitions: Dict[str, Acquisition] = dict()
        self.panoramas: Dict[str, Panorama] = dict()
        self.channels: Dict[str, Channel] = dict()

    @property
    def to_dict(self):
        return self.__dict__

    def save(self, filepath: str):
        with open(filepath, "w") as f:
            yaml.dump(self.to_dict, f)
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"
