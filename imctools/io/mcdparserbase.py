from __future__ import with_statement, division
import xml.etree.ElementTree as et
import struct


class McdParserBase(object):
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
    
    def get_acquisition_buffer(self, ac_id):
        """
        Get the acquisition XML of the acquisition with the id
        :param ac_id: the acquisition id
        :return: the acquisition XML
        """
        f = self._fh
        (data_offset_start, data_size, n_rows, n_channel) = self._acquisition_dict[ac_id][1]
        f.seek(data_offset_start)
        buffer = f.read(data_size)
        return buffer

    def get_acquisition_rawdata(self, ac_id):
        """
        Get the acquisition XML of the acquisition with the id
        :param ac_id: the acquisition id
        :return: the acquisition XML
        """
        f = self._fh
        (data_offset_start, data_size, n_rows, n_channel) = self._acquisition_dict[ac_id][1]
        buffer = self.get_acquisition_buffer(ac_id)
        bufformat = '<'+str(int(n_rows*n_channel)) +'f'
        data = struct.unpack(bufformat, buffer)
        return data

    def get_acquisition_dimensions(self, ac_id):
        """
        Get the number of channels and number of rows

        :return:
        """
        (data_offset_start, data_size, n_rows, n_channel) = self._acquisition_dict[ac_id][1]

        return ( n_rows, n_channel)

    def get_acquisition_channels_xml(self, ac_id):
        """
        Return the Acquisition channel XMLs corresponding to the ID
        :param ac_id:
        :return: acquisition channel xml
        """
        ns = self._ns
        xml = self._xml
        return [channel_xml for channel_xml in xml.findall(ns+'AcquisitionChannel')
                if channel_xml.find(ns+'AcquisitionID').text == ac_id]

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
            channel_name = cxml.find(ns+'ChannelName').text
            order_nr = int(cxml.find(ns+'OrderNumber').text)
            channel_lab = cxml.find(ns+'ChannelLabel').text
            channel_dict.update({order_nr: (channel_name, channel_lab)})

        return channel_dict



    def get_mcd_data(self):
        """
        Uses the offsets encoded in the XML to load the raw data from the mcd.
        """
        acquisition_dict = dict()
        xml = self._xml
        ns = self._ns
        # TODO: There can be different number of channels per acquisition! Check acquisition channel!
        n_channel = int(len(xml.findall(ns+'AcquisitionChannel')))

        for acquisition in xml.findall(ns+'Acquisition'):
            ac_id = acquisition.find(ns+'ID').text
            data_offset_start = int(acquisition.find(ns+'DataStartOffset').text)
            data_offset_end = int(acquisition.find(ns+'DataEndOffset').text)
            data_size = (data_offset_end - data_offset_start + 1)
            n_rows = data_size/ (n_channel*4)
            data_param = (data_offset_start, data_size, n_rows, n_channel)
            acquisition_dict.update({ac_id: (acquisition, data_param)})
        self._acquisition_dict = acquisition_dict

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
        f = self._fh
        xml_start = self._reverse_find_in_buffer(f, start_str.encode('utf-8'))

        if xml_start == -1:
            start_str = self._add_nullbytes(start_str)
            xml_start = self._reverse_find_in_buffer(f, start_str.encode('utf-8'))

        if xml_start == -1:
            raise ValueError('Invalid MCD: MCD xml start tag not found in file %s' % self.file_name)
        else:
            xml_stop = self._reverse_find_in_buffer(f, stop_str.encode('utf-8'))
            if xml_stop == -1:
                stop_str = self._add_nullbytes(stop_str)
                xml_stop = self._reverse_find_in_buffer(f, stop_str.encode('utf-8'))
                # xmls = [mm[start:end] for start, end in zip(xml_starts, xml_stops)]

        if xml_stop == -1:
            raise ValueError('Invalid MCD: MCD xml stop tag not found in file %s' % self.file_name)
        else:
            xml_stop += len(stop_str)

        f.seek(xml_start)
        xml = f.read(xml_stop-xml_start).decode('utf-8')
        xml = xml.replace('\x00','')
        self._xml = et.fromstring(xml)
        self._ns = '{'+self._xml.tag.split('}')[0].strip('{')+'}'


    def get_imc_acquisition(self, ac_id):

        data = self.get_acquisition_rawdata(ac_id)
        nchan = data.shape[1]
        channels = self.get_acquisition_channels(ac_id)
        channel_name, channel_label = zip(*[channels[i] for i in range(nchan)])
        return ImcAcquisition(image_ID=ac_id, original_file=self.filename,
                              data=self.get_acquisition_rawdata(ac_id),
                              channel_names=channel_name,
                              channel_labels=channel_label,
                              original_metadata=str(et.tostring(self._xml, encoding='utf8', method='xml')))

    def close(self):
        """Close the file handle."""
        self._fh.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    @staticmethod
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

    @staticmethod
    def _reverse_find_in_buffer(f, s, buffer_size=4096):
        # based on http://stackoverflow.com/questions/3893885/cheap-way-to-search-a-large-text-file-for-a-string
        f.seek(0, 2)

        buf = None
        overlap = len(s) - 1
        bsize = buffer_size +overlap+1
        f.seek(0, 2)
        cur_pos = f.tell() - bsize
        while cur_pos >=0:
            buf = f.read(bsize)
            if buf:
                pos = buf.find(s)
                if pos >= 0:
                    return f.tell() - (len(buf) - pos)
            cur_pos = f.tell() - 2 * bsize + overlap
            if cur_pos > 0:
                f.seek(cur_pos)
            else:
                return -1


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    fn = '/mnt/imls-bod/data_vito/grade1.mcd'
    with McdParserBase(fn) as testmcd:
        print(testmcd.filename)
        print(testmcd.n_acquisitions)
        # print(testmcd.get_acquisition_xml('0'))
        print(testmcd.get_acquisition_channels_xml('0'))
        print(testmcd.get_acquisition_channels('0'))
        print(len(testmcd.get_acquisition_rawdata('0')))
        # plt.figure()
        # plt.imshow(img.squeeze())
        # plt.show()
        #imc_img.save_image('/mnt/imls-bod/data_vito/test1.tiff')
        # acquisition_dict = get_mcd_data(fn, xml_public)
