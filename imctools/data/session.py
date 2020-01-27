from __future__ import annotations

import yaml
from typing import Any, Dict, Optional

from imctools.data.ablation_image import AblationImage
from imctools.data.acquisition import Acquisition
from imctools.data.channel import Channel
from imctools.data.panorama import Panorama
from imctools.data.slide import Slide


class Session(yaml.YAMLObject):
    """IMC session data"""

    yaml_tag = "!Session"

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

    def __getstate__(self):
        s = self.__dict__.copy()
        return s

    @classmethod
    def from_yaml(cls, loader, node):
        """
        Convert a representation node to a Python object.
        """
        return loader.construct_yaml_object(node, cls)

    @classmethod
    def to_yaml(cls, dumper, data):
        """
        Convert a Python object to a representation node.
        """
        return dumper.represent_yaml_object(cls.yaml_tag, data, cls, flow_style=cls.yaml_flow_style)

    def save(self, filepath: str):
        """Save session data in JSON format

        Parameters
        ----------
        filepath
            output file path

        """
        with open(filepath, "w") as f:
            yaml.dump(self, f)

    @staticmethod
    def load(filepath: str):
        with open(filepath, "r") as f:
            session = yaml.load(f, Loader=yaml.Loader)
            return session

    @property
    def meta_name(self):
        return self.name

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()
    session = Session.load("/home/anton/Downloads/IMMUcan_Batch20191023_10032401-HN-VAR-TIS-01-IMC-01_AC2.yaml")
    print(timeit.default_timer() - tic)
