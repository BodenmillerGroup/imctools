from enum import Enum

from imctools.data.acquisition import Acquisition


class ProgressType(Enum):
    BEFORE = 1
    AFTER = 2


class ProgressImage:
    """
    Progress image
    """

    def __init__(self, acquisition: Acquisition, progress_type: ProgressType, width: int, height: int):
        """
        Parameters
        ----------
        image_type:
            Progress image type (before/after)
        width:
            Image width in pixels
        height:
            Image height in pixels
        """

        self.acquisition = acquisition
        self.progress_type = progress_type
        self.width = width
        self.height = height

    def __repr__(self):
        return f"{self.__class__.__name__}(progress_type={self.progress_type!r})"
