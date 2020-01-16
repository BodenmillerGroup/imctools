from typing import Optional, List

from imctools.data.acquisition import Acquisition
from imctools.data.overview_image import OverviewImage
from imctools.data.session import Session


class Slide:
    """
    Slide
    """

    def __init__(
        self,
        session: Session,
        id: str,
        original_id: int,
        physical_width: float,
        physical_height: float,
        description: Optional[str] = None,
    ):
        """
        Parameters
        ----------
        id:
            Unique slide id per session
        original_id:
            Original slide id
        description:
            Custom slide description
        """

        self.session = session
        self.id = id
        self.original_id = original_id
        self.physical_width = physical_width
        self.physical_height = physical_height
        self.description = description

        self.overview_images: List[OverviewImage] = []
        self.acquisitions: List[Acquisition] = []

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, original_id={self.original_id}, description={self.description})"
        )
