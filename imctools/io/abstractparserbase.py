"""
Creates the basic parser interface
"""
from __future__ import with_statement, division
import array

try:
    xrange
except NameError:
    xrange = range


class AbstractParserBase(object):
    """

    """
    def __init__(self):
        pass

    def get_imc_acquisition(self):
        pass

    @classmethod
    def _reshape_long_2_cyx(self, longdat, is_sorted=True, shape=None, channel_idxs=None):
        """
        Helper method to convert to cxy from the long format.
        Mainly used by during import step
        :param longdat:
        :param is_sorted:
        :param shape:
        :param channel_idxs:
        :param channel_offset:
        :return:
        """
        if shape is None:
            shape = [0, 0]
            for row in longdat:
                if row[0] > shape[0]:
                    shape[0] = int(row[0])
                if row[1] > shape[1]:
                    shape[1] = int(row[1])

            if shape[0]*shape[1] > len(longdat):
                shape[1] -= 1



        if channel_idxs is None:
            channel_idxs = range(len(longdat[0]))

        if is_sorted:
            nchans = len(channel_idxs)
            npixels = shape[0] * shape[1]
            tot_len = npixels * nchans
            imar = array.array('f')

            for i in xrange(tot_len):
                row = i % npixels
                col = channel_idxs[int(i / npixels)]
                imar.append(longdat[row][col])

            img = [[imar[(k * shape[0] * shape[1] + j * shape[0]):(k * shape[0] * shape[1] + j * shape[0] + shape[0])]
                    for j in range(shape[1])]
                   for k in range(nchans)]

        else:
            img = self._initialize_empty_listarray([shape[1],
                                                    shape[0],
                                                    len(channel_idxs)])
            # will be c, y, x
            for row in longdat:
                x = int(row[0])
                y = int(row[1])
                for col, idx in enumerate(channel_idxs):
                    img[col][x][y] = row[idx]

        return img

    @staticmethod
    def _initialize_empty_listarray(shape):
        imar = array.array('f')
        for i in xrange(shape[0] * shape[1] * shape[2]): imar.append(-1.)

        img = [[imar[(k * shape[0] * shape[1] + j * shape[0]):(k * shape[0] * shape[1] + j * shape[0] + shape[0])]
                for j in range(shape[1])]
               for k in range(shape[2])]

        return img