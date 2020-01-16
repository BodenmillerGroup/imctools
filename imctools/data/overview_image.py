from enum import Enum
from typing import Optional, Dict

from imctools.data.slide import Slide


class OverviewImageType(Enum):
    IMPORTED = 1
    INSTRUMENT = 2


class OverviewImage:
    """
    Overview image
    """

    def __init__(
        self,
        slide: Slide,
        original_id: int,
        image_type: OverviewImageType,
        description: str,
        start_position_x: float,
        start_position_y: float,
        width: float,
        height: float,
        rotation_angle: float,
        file_extension: Optional[str] = None,
        meta: Optional[Dict[str, str]] = None,
    ):
        """
        Parameters
        ----------
        width:
            Image width in pixels
        height:
            Image height in pixels
        image_type:
            Progress image type (before/after)
        """

        self.slide = slide
        self.original_id = original_id
        self.image_type = image_type
        self.description = description
        self.start_position_x = start_position_x
        self.start_position_y = start_position_y
        self.width = width
        self.height = height
        self.rotation_angle = rotation_angle
        self.file_extension = file_extension
        self.meta = meta

    def __repr__(self):
        return f"{self.__class__.__name__}(original_id={self.original_id!r}, image_type={self.image_type!r}, description={self.description!r})"
