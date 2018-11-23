from .context import TestMcdParsing

import unittest
import warnings

try:
    import numpy as np
    _have_numpy = True
except ImportError as ix:
    _have_numpy = False

if _have_numpy:
    import imctools.io as imcio
    import numpy as np

    class TestChangeDtype(unittest.TestCase):
        """ Test the the dtype change function """

        def test_uint16(self):
            """
            Test if the uper and lower bounds are correctly
            adjusted.
            """
            testarr = np.array([-10., 100000, 0.3, 0.7])
            testarr_orig = np.copy(testarr)
            target_dtype = np.dtype(np.uint16)
            exp_outarr = np.array([0, (2**16)-1, 0, 1], dtype=target_dtype)
            with warnings.catch_warnings(record=True) as w:
                outarr = imcio.change_dtype(testarr, target_dtype)
                self.assertEqual(len(w), 2, msg='Two truncation warnings should be thrown')
                self.assertEqual(str(w[0].message), imcio.CHANGE_DTYPE_LB_WARNING)
                self.assertEqual(str(w[1].message), imcio.CHANGE_DTYPE_UB_WARNING)
            self.assertEqual(outarr.dtype, target_dtype, msg='Dtype is correctly adapted')
            np.testing.assert_equal(outarr, exp_outarr, err_msg='Trunkating uint16 works')
            np.testing.assert_equal(testarr, testarr_orig, err_msg='The original array is not modified')
