from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from imctools.data.acquisition import Acquisition
from imctools.data.channel import Channel
from imctools.data.panorama import Panorama
from imctools.data.slide import Slide
from ruamel.yaml import YAML


class Session:
    """
    IMC session data

    """
    def __init__(
        self,
        name: str,
        software_version: str,
        origin: str,
        origin_filepath: str,
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

    def save(self, filepath: str):
        yaml = YAML()
        yaml.register_class(Session)
        yaml.register_class(Slide)
        yaml.register_class(Acquisition)
        yaml.register_class(Panorama)
        yaml.register_class(Channel)
        with open(filepath, "wt") as f:
            yaml.dump(self, f)
        pass


    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"
