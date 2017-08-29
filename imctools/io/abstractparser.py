from imctools.io.abstractparserbase import AbstractParserBase
import numpy as np


class AbstractParser(AbstractParserBase):
    def __init__(self):
        AbstractParserBase.__init__(self)

    def _reshape_long_2_cyx(self, longdat, is_sorted=True, shape=None, channel_idxs=None):
        """

        :param longdat:
        :param is_sorted:
        :param shape:
        :param channel_idxs:
        :return:
        """

        if shape is None:
            shape = longdat[:, :2].max(axis=0) + 1
            if np.prod(shape) > longdat.shape[0]:
                shape[1] -= 1

            shape = shape.astype(int)
        if channel_idxs is None:
            channel_idxs = range(longdat.shape[1])
        nchan = len(channel_idxs)

        tdat = longdat[:,channel_idxs]
        assert(longdat.shape[0] == np.prod(shape))
        if is_sorted:
            img = np.reshape(tdat[:(np.prod(shape)),:], [shape[1], shape[0], nchan], order='C')
            img = img.swapaxes(0,2)
            img = img.swapaxes(1, 2)
            return img

        else:
            return NotImplemented



