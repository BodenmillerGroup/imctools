from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID

from imctools.data.slide import Slide


class DataOrigin(Enum):
    MCD_FILE = 1
    TXT_FILE = 2


class Session:
    """
    Session
    """

    def __init__(
        self,
        uid: UUID,
        name: str,
        description: str,
        creation_date: datetime,
        software_version: str,
        data_origin: DataOrigin,
    ):
        """
        Parameters
        ----------
        uid:
            Unique id of the session
        """

        self.uid = uid
        self.name = name
        self.description = description
        self.creation_date = creation_date
        self.software_version = software_version
        self.data_origin = data_origin

        self.slides: List[Slide] = []

    def add_slide(self, slide: Slide):
        self.slides.append(slide)

    def __repr__(self):
        return f"{self.__class__.__name__}(uid={self.uid}, name={self.name}, description={self.description})"
