# read in and display ImagePlus object(s)
from ij import IJ
from loci.plugins import BF
from ij.io import OpenDialog\
from loci.formats import ImageReader
from loci.formats import MetadataTools
import i5d.Image5D

op = OpenDialog('Choose multichannel TIFF')

file = op.getDirectory()+op.getFileName()
imps = BF.openImagePlus(file)
imag = imps[0]
# parse metadata
reader = ImageReader()
omeMeta = MetadataTools.createOMEXMLMetadata()
reader.setMetadataStore(omeMeta)
reader.setId(file)
reader.close()

nchannels = omeMeta.getChannelCount(0)
i5d = i5d.Image5D(omeMeta.getImageName(0), imag.getStack(), nchannels,1,1)
for i in range(nchannels):
	cid =omeMeta.getChannelName(0,i)
	i5d.getChannelCalibration(i+1).setLabel(str(cid))

i5d.setDefaultColors()
i5d.show()



