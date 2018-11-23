import unittest
import platform

try:
    import numpy as np
    _have_numpy = True
except ImportError as ix:
    _have_numpy = False

if _have_numpy:
    from imctools.io import abstractparser

    class BasicTestSuite(unittest.TestCase):
        """Basic test cases."""
        def test_reshape_long_2_cxy(self):
            """
            Assert that the reshaping from long to cxy image goes correctly in the numpy based reshaping
            :return:
            """

            abstparser = abstractparser.AbstractParser()
            self._reshape_tests(abstparser.reshape_long_2_cyx)

        def _reshape_tests(self, reshape_fkt, nrow=10, ncol=20):
            """
            Tests the resphaping based on some ad hoc testdata
            :param reshape_fkt:
            :param nrow:
            :param ncol:
            :return:
            """
            chan_4 = 1

            test_longdat = np.array([[i % ncol, int(i / ncol), i, chan_4] for i in range(nrow * ncol)])
            img = reshape_fkt(test_longdat, is_sorted=True)
            np.testing.assert_array_equal(np.asarray(img[0]), np.asarray([[float(j) for j in range(ncol)] for i in range(nrow)]))
            np.testing.assert_array_equal(np.asarray(img[1]), np.asarray([[float(i) for j in range(ncol)] for i in range(nrow)]))
            np.testing.assert_array_equal(np.asarray(img[2]), np.asarray([[float(i*ncol+j) for j in range(ncol)] for i in range(nrow)]))
            np.testing.assert_array_equal(np.asarray(img[3]), np.asarray([[float(1) for j in range(ncol)] for i in range(nrow)]))
