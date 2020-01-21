import numpy as np

from imctools.io.utils import reshape_long_2_cyx


def test_reshape_long_2_cxy(nrow=10, ncol=20):
    """Tests data reshaping based on some ad hoc test data

    """
    chan_4 = 1

    test_longdat = np.array([[i % ncol, int(i / ncol), i, chan_4] for i in range(nrow * ncol)])
    img = reshape_long_2_cyx(test_longdat, is_sorted=True)
    np.testing.assert_array_equal(np.asarray(img[0]),
                                  np.asarray([[float(j) for j in range(ncol)] for i in range(nrow)]))
    np.testing.assert_array_equal(np.asarray(img[1]),
                                  np.asarray([[float(i) for j in range(ncol)] for i in range(nrow)]))
    np.testing.assert_array_equal(np.asarray(img[2]),
                                  np.asarray([[float(i * ncol + j) for j in range(ncol)] for i in range(nrow)]))
    np.testing.assert_array_equal(np.asarray(img[3]),
                                  np.asarray([[float(1) for j in range(ncol)] for i in range(nrow)]))
