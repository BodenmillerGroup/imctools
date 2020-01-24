import abc

from imctools.data import Session


class ParserBase(abc.ABC):

    @property
    @abc.abstractmethod
    def origin(self) -> str:
        """Save the data object to the output."""
        raise NotImplemented

    @property
    @abc.abstractmethod
    def session(self) -> Session:
        """Save the data object to the output."""
        raise NotImplemented

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
