from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from yaml import YAMLObject, load, dump
# In order to use LibYAML based parser and emitter, use the classes CParser and CEmitter.
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from imctools.data.ablation_image import AblationImage
from imctools.data.acquisition import Acquisition
from imctools.data.channel import Channel
from imctools.data.panorama import Panorama
from imctools.data.slide import Slide


class Session(YAMLObject):
    """IMC session data. Container for all slides, acquisitions, panoramas, etc."""

    yaml_tag = "!Session"

    def __init__(
        self,
        id: str,
        name: str,
        imctools_version: str,
        origin: str,
        source_path: str,
        created: datetime,
        metadata: Optional[Dict[str, Any]] = None,
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
        origin
            Data origin (mcd, txt, ome-tiff, etc)
        source_path
            Path to the original data source
        created
            Datetime of session creation
        metadata
            Whole set of original (raw) metadata as a dictionary
        """
        self.id = id
        self.name = name
        self.imctools_version = imctools_version
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
        """Returns dictionary for JSON/YAML serialization"""
        s = self.__dict__.copy()
        return s

    @classmethod
    def from_yaml(cls, loader, node):
        """Convert a representation node to a Python object."""
        return loader.construct_yaml_object(node, cls)

    @classmethod
    def to_yaml(cls, dumper, data):
        """Convert a Python object to a representation node."""
        return dumper.represent_yaml_object(cls.yaml_tag, data, cls, flow_style=cls.yaml_flow_style)

    def save(self, filepath: str):
        """Save session data in YAML format

        Parameters
        ----------
        filepath
            Output YAML file path
        """
        with open(filepath, "w") as f:
            dump(self, f, sort_keys=False)

    @staticmethod
    def load(filepath: str):
        """Load IMC session data from YAML file

        Parameters
        ----------
        filepath
            Input YAML file path
        """
        with open(filepath, "r") as f:
            session = load(f, Loader=Loader)
            session = Session._rebuild_object_tree(session)
            return session

    @staticmethod
    def _rebuild_object_tree(se: Session):
        """Helper function that re-creates parents/children relations between entities"""
        for sl in se.slides.values():
            sl.session = se

        for pa in se.panoramas.values():
            sl = se.slides.get(pa.slide_id)
            if not hasattr(sl, "panoramas"):
                sl.panoramas = dict()
            sl.panoramas[pa.id] = pa
            pa.slide = sl

        for ac in se.acquisitions.values():
            sl = se.slides.get(ac.slide_id)
            if not hasattr(sl, "acquisitions"):
                sl.acquisitions = dict()
            sl.acquisitions[ac.id] = ac
            ac.slide = sl

        for ch in se.channels.values():
            ac = se.acquisitions.get(ch.acquisition_id)
            if not hasattr(ac, "channels"):
                ac.channels = dict()
            ac.channels[ch.id] = ch
            ch.acquisition = ac
        return se

    @property
    def meta_name(self):
        """Meta name fully describing the entity"""
        return self.name

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()
    session = Session.load("/home/anton/Downloads/IMMUcan_Batch20191023_10032401-HN-VAR-TIS-01-IMC-01_AC2.yaml")
    print(timeit.default_timer() - tic)
