# read in and display ImagePlus object(s)
from ij import IJ
from loci.plugins import BF
from ij.io import OpenDialog
from loci.formats import ImageReader
from loci.formats import MetadataTools
import i5d.Image5D
import i5d


def load_img(file_name):
    """

    :param file_name:
    :return:
    """
    imps = BF.openImagePlus(file_name)
    imag = imps[0]
    # parse metadata
    reader = ImageReader()
    omeMeta = MetadataTools.createOMEXMLMetadata()
    reader.setMetadataStore(omeMeta)
    reader.setId(file_name)
    reader.close()

    return (imag, omeMeta)


def view_image5d_ome(img, ome_meta):
    """

    :param img:
    :param ome_meta:
    :return:
    """
    nchannels = ome_meta.getChannelCount(0)
    channel_names = [ome_meta.getChannelName(0,i) for i in range(nchannels)]
    view_image5d(imgName=ome_meta.getImageName(0),
                 img_stack=img.getStack(),
                 nchannels=ome_meta.getChannelCount(0),
                 channel_names = channel_names)

def view_image5d(imgName, img_stack, nchannels, channel_names):
    """

    :param imgName:
    :param img_stack:
    :param nchannels:
    :param channel_names:
    :return:
    """
    i5dimg = i5d.Image5D(imgName, img_stack, nchannels,1,1)
    for i in range(nchannels):
        cid =channel_names[i]
        i5dimg.getChannelCalibration(i+1).setLabel(str(cid))

    i5dimg.setDefaultColors()
    i5dimg.show()

def load_and_view(file_name):
    (imag, omeMeta) = load_img(file_name)
    view_image5d_ome(imag, omeMeta)


if __name__ == '__main__':
    op = OpenDialog('Choose multichannel TIFF')
    file = op.getDirectory() + op.getFileName()
    load_and_view(file_name=file)