import numpy as np
import mmap
import xml.etree.ElementTree as et

from imctools.io.imcacquisition import ImcAcquisition

class McdParser(object):
    """Parsing data from Fluidigm MCD files

    The McdParser object should be closed using the close
    :param object:
    :return:
    """
    
    def __init__(self, file_name):
        """

        :param file_name:
        """
        self._fh = open(file_name, mode='rb')
        self._xml = None
        self._ns = None
        self._acquisition_dict = None

        self.retrieve_mcd_xml()
        self.get_mcd_data()

    @property
    def filename(self):
        "Return the name of the open file"
        return self._fh.name

    @property
    def n_acquisitions(self):
        """
        Number of acquisitions in the file
        :return:
        """
        return len(self._acquisition_dict.keys())

    @property
    def acquisition_ids(self):
        """
        Acquisition IDs
        :return:
        """
        return self._acquisition_dict.keys()

    def get_acquisition_xml(self, ac_id):
        """
        Get the acquisition XML of the acquisition with the id
        :param ac_id: the acquisition id
        :return: the acquisition XML
        """
        return self._acquisition_dict[ac_id][0]

    def get_acquisition_rawdata(self, ac_id):
        """
        Get the acquisition XML of the acquisition with the id
        :param ac_id: the acquisition id
        :return: the acquisition XML
        """
        return np.array(self._acquisition_dict[ac_id][1])

    def get_acquisition_channels_xml(self, ac_id):
        """
        Return the Acquisition channel XMLs corresponding to the ID
        :param ac_id:
        :return: acquisition channel xml
        """
        ns = self._ns
        xml = self._xml
        return [channel_xml for channel_xml in xml.findall('ns:AcquisitionChannel', ns)
                        if channel_xml.find('ns:AcquisitionID', ns).text == ac_id]

    def get_acquisition_channels(self, ac_id):
        """
        Returns a dict with the channel metadata
        :param ac_id: acquisition ID
        :return: dict with key: channel_nr, value: (channel_name, channel_label)
        """
        ns = self._ns
        channel_xmls = self.get_acquisition_channels_xml(ac_id)
        channel_dict = dict()
        for cxml in channel_xmls:
            channel_name = cxml.find('ns:ChannelName', ns).text
            order_nr = int(cxml.find('ns:OrderNumber', ns).text)
            channel_lab = cxml.find('ns:ChannelLabel', ns).text
            channel_dict.update({order_nr: (channel_name, channel_lab)})

        return channel_dict

    def get_acquisition_imagestack(self, ac_id):

        ge

    @property
    def xml(self):
        return self._xml

    def retrieve_mcd_xml(self, start_str='<MCDSchema', stop_str='</MCDSchema>'):
        """
        Finds the MCD metadata XML in the binary.
        As suggested in the specifications the file is parsed from the end.

        :param fn:
        :param start_str:
        :param stop_str:
        :return:
        """

        mm = mmap.mmap(self._fh.fileno(), 0, prot=mmap.PROT_READ)

        xml_start = mm.rfind(start_str.encode('utf-8'))

        if xml_start == -1:
            start_str = _add_nullbytes(start_str)
            xml_start = mm.rfind(start_str.encode('utf-8'))

        if xml_start == -1:
            raise ValueError('Invalid MCD: MCD xml start tag not found in file %s' % self.file_name)
        else:
            xml_stop = mm.rfind(stop_str.encode('utf-8'))
            if xml_stop == -1:
                stop_str = _add_nullbytes(stop_str)
                xml_stop = mm.rfind(stop_str.encode('utf-8'))
                # xmls = [mm[start:end] for start, end in zip(xml_starts, xml_stops)]

        if xml_stop == -1:
            raise ValueError('Invalid MCD: MCD xml stop tag not found in file %s' % self.file_name)
        else:
            xml_stop += len(stop_str)

        xml = mm[xml_start:xml_stop].decode('utf-8')
        self._xml = et.fromstring(xml)
        self._ns = {'ns': self._xml.tag.split('}')[0].strip('{')}

    def get_mcd_data(self):
        """
        Uses the offsets encoded in the XML to load the raw data from the mcd.
        """
        acquisition_dict = dict()
        xml = self._xml
        ns = self._ns
        
        n_channel = int(len(xml.findall('ns:AcquisitionChannel', ns)))

        for acquisition in xml.findall('ns:Acquisition',ns):
            ac_id = acquisition.find('ns:ID', ns).text
            data_offset_start = int(acquisition.find('ns:DataStartOffset', ns).text)
            data_offset_end = int(acquisition.find('ns:DataEndOffset', ns).text)
            data_size = (data_offset_end - data_offset_start + 1) / 4
            n_rows = data_size / n_channel
            data = np.memmap(self._fh, dtype='<f', mode='r', offset=data_offset_start,
                             shape=(int(n_rows), n_channel))
            acquisition_dict.update({ac_id: (acquisition, data)})

        self._acquisition_dict = acquisition_dict

    def get_imc_acquisition(self, ac_id):

        data = self.get_acquisition_rawdata(ac_id)
        nchan = data.shape[1]
        channels = self.get_acquisition_channels(ac_id)
        channel_name, channel_label = zip(*[channels[i] for i in range(nchan)])
        return ImcAcquisition(image_ID=ac_id, original_file=self.filename,
                              data=self.get_acquisition_rawdata(ac_id),
                              channel_names=channel_name,
                              channel_labels=channel_label,
                              original_metadata= str(et.tostring(self._xml, encoding='utf8', method='xml')))
    
    def close(self):
        """Close the file handle."""
        self._fh.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


def _add_nullbytes(buffer_str):
    """
    Adds nullbits between letters.

    :param buffer_str:
    :return: string with nullbits

    >>> _add_nullbytes('abc')
    'a\\x00b\\x00c\\x00'
    """
    pad_str = ''
    for s in buffer_str:
        pad_str += s + '\x00'
    return pad_str



if __name__ == '__main__':


    import matplotlib.pyplot as plt
    fn = '/mnt/imls-bod/data_vito/grade1.mcd'
    with McdParser(fn) as testmcd:
        print(testmcd.filename)
        print(testmcd.n_acquisitions)
        #print(testmcd.get_acquisition_xml('0'))
        print(testmcd.get_acquisition_channels_xml('0'))
        print(testmcd.get_acquisition_channels('0'))
        imc_img = testmcd.get_imc_acquisition('0')
        img = imc_img.get_img_stack()
        img = imc_img.get_img_by_name('X')
        # plt.figure()
        # plt.imshow(img.squeeze())
        # plt.show()
        imc_img.save_image('/mnt/imls-bod/data_vito/test1.tiff')
    #acquisition_dict = get_mcd_data(fn, xml_public)