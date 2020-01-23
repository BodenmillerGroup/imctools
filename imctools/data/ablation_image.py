from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from imctools.data.acquisition import Acquisition


class AblationImageType(Enum):
    BEFORE = "before"
    AFTER = "after"


class AblationImage:
    """Ablation image (before/after)

    """

    def __init__(self, acquisition_id: int, image_type: AblationImageType, filename: str):
        self.acquisition_id = acquisition_id
        self.image_type = image_type
        self.filename = filename

        self.acquisition: Optional[Acquisition] = None

    @property
    def meta_name(self):
        parent_name = self.acquisition.meta_name
        return f"{parent_name}_{self.image_type}_ablation"

    def to_dict(self):
        """Returns dictionary for JSON/YAML serialization"""
        d = self.__dict__.copy()
        d.pop("acquisition")
        return d

    def __repr__(self):
        return f"{self.__class__.__name__}(acquisition_id={self.acquisition_id}, image_type={self.image_type}, filename={self.filename})"
