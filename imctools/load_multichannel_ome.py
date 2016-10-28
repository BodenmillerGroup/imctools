# read in and display ImagePlus object(s)
from ij.io import OpenDialog
import os

from imctools.imagej import library as lib

def view_image5d_ome(img, ome_meta):
    """

    :param img:
    :param ome_meta:
    :return:
    """
    nchannels = ome_meta.getChannelCount(0)
    channel_names = [ome_meta.getChannelName(0,i) for i in range(nchannels)]
    img = lib.get_image5d(imgName=ome_meta.getImageName(0),
                 img_stack=img.getStack(),
                 channel_names = channel_names)
    img.show()

def load_and_view(file_name):
    (imag, omeMeta) = lib.load_ome_img(file_name)
    view_image5d_ome(imag, omeMeta)


if __name__ == '__main__':
    op = OpenDialog('Choose multichannel TIFF')
    file = os.path.join(op.getDirectory(), op.getFileName())
    load_and_view(file_name=file)