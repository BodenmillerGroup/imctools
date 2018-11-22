import warnings

CHANGE_DTYPE_LB_WARNING = 'Data minimum trunkated as outside dtype range'
CHANGE_DTYPE_UB_WARNING = 'Data max trunkated as outside dtype range'

# Checks if numpy is available in the
# Python implementation

try:
    import numpy as np
    _have_np = True
except ImportError:
    _have_np = False

if _have_np:
    def change_dtype(array, dtype):
        """
        Changes the dtype of an array

        This makes sure that the values are correctly truncated and rounded
        to fit into the new dtype.

        :param array: a numpy array
        :param dtypw: a numpy dtype
        :returns: a copy of the array with the correct dtype.
        """
        if dtype.kind in ['i', 'u']:
            dinf = np.iinfo(dtype)
            array = np.around(array)
            mina = array.min()
            maxa = array.max()
            t_min = None
            t_max = None
            if mina < dinf.min:
                t_min = dinf.min
                warnings.warn(CHANGE_DTYPE_LB_WARNING)

            if maxa > dinf.max:
                t_max = dinf.max
                warnings.warn(CHANGE_DTYPE_UB_WARNING)
            if (t_min is not None) | (t_max is not None):
                # this can be done inplace, as np.around returns array new object.
                np.clip(array, a_min=t_min, a_max=t_max, out=array)
        array = array.astype(dtype)
        return array
