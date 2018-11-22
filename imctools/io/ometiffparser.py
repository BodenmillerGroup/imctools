import tifffile
import xml.etree.ElementTree as et

from imctools.io.abstractparser import AbstractParser
from imctools.io.imcacquisition import ImcAcquisition


class OmetiffParser(AbstractParser):
    """
    Parses an ome tiff
    """

    def __init__(self, original_file, origin='ome.tiff'):
        """

        :param filename:
        """
        AbstractParser.__init__(self)

        (data,ome) = self._read_image(original_file)
        self.data = data
        self.ome = et.fromstring(ome)

        self.filename = original_file
        self.n_acquisitions = 1
        self.origin = origin

        self.ns = '{' + self.ome.tag.split('}')[0].strip('{') + '}'
        self.get_meta_dict()

    def get_imc_acquisition(self):
        """
        Get Imc Acquisition object

        :return:
        """
        meta = self.meta_dict
        return ImcAcquisition(meta['image_ID'],
                              self.original_file,
                              self.data,
                              meta['channel_metals'],
                              meta['channel_labels'],
                              original_metadata=self.ome ,
                              image_description=None,
                              origin=self.origin,
                              offset=0)

    def get_meta_dict(self):
        meta_dict = dict()

        xml = self.ome
        ns = self.ns
        img = xml.find(ns+'Image')
        pixels = img.find(ns+'Pixels')
        channels = pixels.findall(ns+'Channel')
        nchan = len(channels)
        chan_dict={int(chan.attrib['ID'].split(':')[2]) :
                       (chan.attrib['Name'], chan.attrib['Fluor']) for chan in channels}

        meta_dict.update({'image_ID': img.attrib['Name'],
                          'channel_metals': [chan_dict[i][1] for i in range(nchan)],
                          'channel_labels': [chan_dict[i][0] for i in range(nchan)]})

        self.meta_dict = meta_dict

    
    def _read_image(self, filename):
        with tifffile.TiffFile(filename) as tif:
            try:
                data = tif.asarray(out='memmap')
            except:
                # this is in an older tifffile version is used
                data = tif.asarray()
            try:
                ome = tif.pages[0].tags['ImageDescription'].value
            except:
                ome = tif.pages[0].tags['image_description'].value
            return(data,ome)
