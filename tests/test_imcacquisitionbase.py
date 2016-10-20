import unittest
from imctools.io import imcacquisitionbase
import numpy as np

class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_reshape_long_2_cxy(self):
        """
        Assert that the reshaping from long to cxy image goes correctly
        :return:
        """

        nrow = 10
        ncol = 3
        nchan = 4
        chan_4 = 1

        test_longdat = [[i%ncol, int(i/ncol), i, chan_4] for i in range(nrow*ncol)]

        print(test_longdat)
        imc_ac = imcacquisitionbase.ImcAcquisitionBase('test','test',test_longdat, channel_labels=None,
                                                       channel_metal=None, is_long=True)
        np.testing.assert_array_equal(np.asarray(imc_ac.get_img_by_channel_nr(0)), np.asarray([[float(j) for j in range(ncol)] for i in range(nrow)]))
        np.testing.assert_array_equal(np.asarray(imc_ac.get_img_by_channel_nr(1)), np.asarray([[float(i) for j in range(ncol)] for i in range(nrow)]))
        np.testing.assert_array_equal(np.asarray(imc_ac.get_img_by_channel_nr(2)), np.asarray([[float(i*ncol+j) for j in range(ncol)] for i in range(nrow)]))
        np.testing.assert_array_equal(np.asarray(imc_ac.get_img_by_channel_nr(3)), np.asarray([[float(1) for j in range(ncol)] for i in range(nrow)]))