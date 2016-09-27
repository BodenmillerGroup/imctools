from imctools.io.imcacquisition import ImcAcquisitionBase
from imctools.io.abstractparser import AbstractParser
import xml.etree.ElementTree as et

class OmeParserBase(AbstractParser):
    def __init__(self, data, ome, original_file=None, origin=None):
        """

        :param filename:
        """
        super(OmeParserBase, self).__init__()
        if origin is None:
            origin = 'ome'
        self.ome = et.fromstring(ome)
        self.ns = '{' + self.ome.tag.split('}')[0].strip('{') + '}'
        self.data = data
        self.get_meta_dict()
        self.original_file = original_file
        self.origin = origin

    def get_imc_aquisition(self):
        meta = self.meta_dict
        return ImcAcquisitionBase(meta['image_ID'],
                                                    self.original_file,
                                                    self.data,
                                                    meta['channel_metals'],
                                                    meta['channel_labels'],
                                                    original_metadata=self.ome ,
                                                    image_description=None,
                                                    origin=self.origin)

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