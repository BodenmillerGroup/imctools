from datetime import datetime
from enum import Enum
from typing import Dict
from uuid import UUID

from imctools.data.slide import Slide


class Session:
    """
    Session

    """

    def __init__(
        self,
        name: str,
        description: str,
        creation_date: datetime,
        software_version: str,
        data_origin: str,
        origin_path: str
    ):
        self.name = name
        self.description = description
        self.creation_date = creation_date
        self.software_version = software_version
        self.data_origin = data_origin
        self.origin_path = origin_path

        self.slides: Dict[str, Slide] = dict()

    def __repr__(self):
        return f"{self.__class__.__name__}(uid={self.uid}, name={self.name}, description={self.description})"
