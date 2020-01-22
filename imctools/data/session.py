from __future__ import annotations

from typing import Dict, Optional, Any

from imctools.data.ablation_image import AblationImage
from imctools.data.acquisition import Acquisition
from imctools.data.channel import Channel
from imctools.data.panorama import Panorama
from imctools.data.slide import Slide

import json


class Session:
    """IMC session data

    """

    def __init__(
        self,
        name: str,
        software_version: str,
        origin: str,
        origin_path: str,
        created_at: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.id = "0"
        self.name = name
        self.software_version = software_version
        self.origin = origin
        self.origin_path = origin_path
        self.created_at = created_at
        self.metadata = metadata

        self.slides: Dict[str, Slide] = dict()
        self.acquisitions: Dict[str, Acquisition] = dict()
        self.panoramas: Dict[str, Panorama] = dict()
        self.channels: Dict[str, Channel] = dict()
        self.ablation_images: Dict[str, AblationImage] = dict()

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

    @property
    def meta_name(self):
        return self.name

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"
