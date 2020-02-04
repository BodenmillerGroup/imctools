import abc

from imctools.data import Session, Optional


class ParserBase(abc.ABC):
    """Abstract base parser class"""

    @property
    @abc.abstractmethod
    def origin(self) -> str:
        """Data origin type, like `txt`, `mcd`, etc."""
        raise NotImplemented

    @property
    @abc.abstractmethod
    def session(self) -> Session:
        """Session data as a container for all slides, panoramas, acquisitions and other data types."""
        raise NotImplemented

    def get_mcd_xml(self) -> Optional[str]:
        """Original (raw) metadata from MCD file in XML format."""
        return None

    def save_artifacts(self, output_folder: str):
        """Override this method in order to support writing parser-specific data to IMC compatible folder.

        Example: before/after ablation images, panorama images, etc.
        """
        pass

    def close(self):
        """Override this method in order to support context manager resource disposal"""
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
