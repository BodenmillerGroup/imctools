import abc

class AbstractParser(object):
    """

    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    def get_imc_acquisition(self):
        return None



