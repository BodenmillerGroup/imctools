from imctools.io.imcacquisition import ImcAcquisition
from imctools.io.imcacquisitionomebase import ImcAcquisitionOmeBase
import tifffile
import numpy as np
import xml.etree.ElementTree as et


class ImcAcquisitionOmeTiff(ImcAcquisitionOmeBase):
    """
     An Image Acquisition Object representing a single acquisition

    """

    def __init__(self, original_file):
        """

        :param filename:
        """
        self.read_image(original_file)

        # reshape it to the stupid format
        print(self._data.shape)
        self._data = self.reshape_flat(self._data)
        ImcAcquisitionOmeBase.__init__(self, self._data, self._ome)

    def read_image(self, filename):
        with tifffile.TiffFile(filename) as tif:
            self._data = tif.asarray()
            print(tif._ome_series())
            print(tif.is_ome)
            self._ome = tif.pages[0].tags['image_description'].value

    @staticmethod
    def reshape_flat(data):
        print(data[0,0,:5])
        c, y, x = data.shape
        h = x * y
        data = np.reshape(data.ravel(order='C'),(h, c), order='F')
        data = np.hstack((np.tile(np.arange(x),y).reshape((h,1)),
                          np.repeat(np.arange(y),x).reshape((h,1)),
                          (np.arange(h)+1).reshape((h, 1)),
                          data))
        print(data[:5,3])
        return data

if __name__ == '__main__':
    fn = '/home/vitoz/temp/test.ome.tiff'
    imc_ac = ImcAcquisitionOmeTiff(fn)
    print(imc_ac._data.shape)
    import matplotlib.pyplot as plt
    plt.figure()
    dat = np.array(imc_ac.get_img_stack_cyx([0])).squeeze()
    plt.imshow(np.array(imc_ac.get_img_stack_cyx([0])).squeeze())
    plt.show()
    print(imc_ac.channel_names)