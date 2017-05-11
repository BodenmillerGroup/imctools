import numpy as np
import mmap
import xml.etree.ElementTree as et

from imctools.io.mcdparserbase import McdParserBase
from imctools.io.imcacquisition import ImcAcquisition
from imctools.io.abstractparser import AbstractParser

"""
Extends the McdParser to make use of numpy and memorymaps
"""


class McdParser(AbstractParser, McdParserBase):
    """Parsing data from Fluidigm MCD files

    The McdParser object should be closed using the close
    :param object:
    :return:
    """
    
    def __init__(self, filename, filehandle=None):
        """

        :param filename:
        """
        McdParserBase.__init__(self, filename, filehandle)
        AbstractParser.__init__(self)

    def get_acquisition_rawdata(self, ac_id):
        """
        Get the acquisition XML of the acquisition with the id
        :param ac_id: the acquisition id
        :return: the acquisition XML
        """
        return np.array(self._acquisition_dict[ac_id][1])

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
            raise ValueError('Invalid MCD: MCD xml start tag not found in file %s' % self.filename)
        else:
            xml_stop = mm.rfind(stop_str.encode('utf-8'))
            if xml_stop == -1:
                stop_str = _add_nullbytes(stop_str)
                xml_stop = mm.rfind(stop_str.encode('utf-8'))
                # xmls = [mm[start:end] for start, end in zip(xml_starts, xml_stops)]

        if xml_stop == -1:
            raise ValueError('Invalid MCD: MCD xml stop tag not found in file %s' % self.filename)
        else:
            xml_stop += len(stop_str)

        xml = mm[xml_start:xml_stop].decode('utf-8')
        self._xml = et.fromstring(xml)
        self._ns = '{' + self._xml.tag.split('}')[0].strip('{') + '}'

    def get_mcd_data(self):
        """
        Uses the offsets encoded in the XML to load the raw data from the mcd.
        """
        acquisition_dict = dict()
        xml = self._xml
        ns = self._ns

        for acquisition in xml.findall(ns+'Acquisition'):
            ac_id = acquisition.find(ns+'ID').text
            n_channel = self.get_nchannels_acquisition(ac_id)
            data_offset_start = int(acquisition.find(ns+'DataStartOffset').text)
            data_offset_end = int(acquisition.find(ns+'DataEndOffset').text)
            data_size = (data_offset_end - data_offset_start + 1) / 4
            n_rows = data_size / n_channel
            data = np.memmap(self._fh, dtype='<f', mode='r',
                             offset=data_offset_start,
                             shape=(int(n_rows), n_channel))
            acquisition_dict.update({ac_id: (acquisition, data)})

        self._acquisition_dict = acquisition_dict

    def get_imc_acquisition(self, ac_id):

        data = self.get_acquisition_rawdata(ac_id)
        nchan = data.shape[1]
        channels = self.get_acquisition_channels(ac_id)
        channel_name, channel_label = zip(*[channels[i] for i in range(nchan)])
        img = self._reshape_long_2_cyx(data, is_sorted=True)
        return ImcAcquisition(image_ID=ac_id, original_file=self.filename,
                              data=img,
                              channel_metal=channel_name,
                              channel_labels=channel_label,
                              original_metadata= str(et.tostring(self._xml, encoding='utf8', method='xml')),
                              offset=3)

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
    fn = '/mnt/imls-bod/Daniel_Data/August/large_CXCL13_CXCL13_UBC_image/CXCL13_CXCL10_UBC.mcd'
    #fn = '/mnt/imls-bod/Daniel_Data/September/02/Her2_grade0/grade_0.mcd'
    with McdParser(fn) as testmcd:
        print(testmcd.filename)
        print(testmcd.n_acquisitions)
        print(testmcd.acquisition_ids)
        print(testmcd.get_acquisition_channels_xml(testmcd.acquisition_ids[0]))
        print(testmcd.get_acquisition_channels(testmcd.acquisition_ids[0]))
        imc_img = testmcd.get_imc_acquisition(testmcd.acquisition_ids[0])
        img = imc_img.get_img_stack_cyx()
        img = imc_img.get_img_by_metal('X')
        plt.figure()
        plt.imshow(img.squeeze())
        plt.show()
        #imc_img.save_image('/mnt/imls-bod/data_vito/test1.tiff')
    #acquisition_dict = get_mcd_data(fn, xml_public)
