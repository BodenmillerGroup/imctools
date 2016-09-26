from imctools.io.imcacquisition import ImcAcquisitionBase
import xml.etree.ElementTree as et

class ImcAcquisitionOmeBase(ImcAcquisitionBase):
    def __init__(self, data, ome, original_file=None, origin=None):
        """

        :param filename:
        """
        if origin is None:
            origin = 'ome'
        self._ome = et.fromstring(ome)
        self._ns = '{' + self._ome.tag.split('}')[0].strip('{') + '}'
        self._data = data
        self.get_meta_dict()
        meta = self.meta_dict
        super(ImcAcquisitionOmeBase, self).__init__( meta['image_ID'],
                                                    original_file,
                                                    data,
                                                    meta['channel_names'],
                                                    meta['channel_labels'],
                                                    original_metadata=ome,
                                                    image_description=None,
                                                    origin=origin)

    def get_meta_dict(self):
        meta_dict = dict()

        xml = self._ome
        ns = self._ns
        img = xml.find(ns+'Image')
        pixels = img.find(ns+'Pixels')
        channels = pixels.findall(ns+'Channel')
        nchan = len(channels)
        chan_dict={int(chan.attrib['ID'].split(':')[2]) :
                       (chan.attrib['Name'], chan.attrib['Fluor']) for chan in channels}

        meta_dict.update({'image_ID': img.attrib['Name'],
                          'channel_names': [chan_dict[i][1] for i in range(nchan)],
                          'channel_labels': [chan_dict[i][0] for i in range(nchan)]})

        self.meta_dict = meta_dict