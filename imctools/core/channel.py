from typing import Optional, Dict

from imctools.core.acquisition import Acquisition


class Channel:
    """
    Image channel
    """

    def __init__(
        self,
        acquisition: Acquisition,
        id: str,
        original_id: int,
        tag: str,
        description: Optional[str] = None,
        meta: Optional[Dict[str, str]] = None,
    ):
        """
        Parameters
        ----------
        id:
            Unique channel id
        original_id:
            Original channel id
        tag:
            Unique channel tag (Metal)(Mass)
        description:
            Custom channel description
        meta:
            Raw metadata
        """

        self.acquisition = acquisition
        self.id = id
        self.original_id = original_id
        self.tag = tag
        self.description = description
        self.meta = meta

    def __repr__(self):
        return f"{self.__class__.__name__}(original_id={self.original_id!r}, tag={self.tag!r}, description={self.description!r})"
