import numpy as np
import mmap
import xml.etree.ElementTree as et

from imctools.io.mcdparserbase import McdParserBase
from imctools.io.imcacquisition import ImcAcquisition
from imctools.io.abstractparser import AbstractParser
from imctools.io.abstractparserbase import AcquisitionError
from imctools.io.mcdxmlparser import McdXmlParser
import imctools.io.mcdxmlparser as mcdmeta


class McdParser:
    def __init__(self, filename, filehandle=None, metafilename=None):
        """
        Initializes the MCDparser object
        :param filename: a filename of an .mcd file
        :param filehandle: a filehandle pointing to an open .mcd file
        :returns: the mcdparser object
        """
        McdParserBase.__init__(self, filename, filehandle, metafilename)
        AbstractParser.__init__(self)

    def get_acquisition_rawdata(self, ac_id):
        """
        Gets the unreshaped image data from the acquisition.
        :param ac_id: the acquisition id
        :returns: the acquisition rawdata
        """
        ac = self.meta.get_acquisitions()[ac_id]
        data_offset_start = ac.data_offset_start
        data_offset_end = ac.data_offset_end
        data_size = ac.data_size
        n_rows = ac.data_nrows
        n_channel = ac.n_channels

        if n_rows == 0:
            raise AcquisitionError('Acquisition ' + ac_id + ' emtpy!')

        data = np.memmap(self._fh, dtype='<f', mode='r',
                             offset=data_offset_start,
                             shape=(int(n_rows), n_channel))
        return data

    def retrieve_mcd_xml(self, start_str='<MCDSchema', stop_str='</MCDSchema>'):
        """
        Finds the MCD metadata XML in the binary and updates the mcdparser object.
        As suggested in the specifications the file is parsed from the end.

        :param fn:
        :param start_str:
        :param stop_str:
        """
        mm = mmap.mmap(self._metafh.fileno(), 0, access=mmap.ACCESS_READ)

        xml_start = mm.rfind(start_str.encode('utf-8'))

        if xml_start == -1:
            start_str = self._add_nullbytes(start_str)
            xml_start = mm.rfind(start_str.encode('utf-8'))

        if xml_start == -1:
            raise ValueError('Invalid MCD: MCD xml start tag not found in file %s' % self.filename)
        else:
            xml_stop = mm.rfind(stop_str.encode('utf-8'))
            if xml_stop == -1:
                stop_str = self._add_nullbytes(stop_str)
                xml_stop = mm.rfind(stop_str.encode('utf-8'))
                # xmls = [mm[start:end] for start, end in zip(xml_starts, xml_stops)]

        if xml_stop == -1:
            raise ValueError('Invalid MCD: MCD xml stop tag not found in file %s' % self.filename)
        else:
            xml_stop += len(stop_str)

        xml = mm[xml_start:xml_stop].decode('utf-8')
        # This is for mcd schemas, where the namespace are often messed up.
        xml = xml.replace('diffgr:','').replace('msdata:','')
        self._xml = et.fromstring(xml)
        self._ns = '{' + self._xml.tag.split('}')[0].strip('{') + '}'

    def get_imc_acquisition(self, ac_id, ac_description=None):
        """
        Returns an ImcAcquisition object corresponding to the ac_id
        :param ac_id: The requested acquisition id
        :returns: an ImcAcquisition object
        """

        data = self.get_acquisition_rawdata(ac_id)
        nchan = data.shape[1]
        channels = self.get_acquisition_channels(ac_id)
        channel_name, channel_label = zip(*[channels[i] for i in range(nchan)])
        img = self._reshape_long_2_cyx(data, is_sorted=True)
        if ac_description is None:
            ac_description = self.meta.get_object(mcdmeta.ACQUISITION, ac_id).metaname

        return ImcAcquisition(image_ID=ac_id, original_file=self.filename,
                              data=img,
                              channel_metal=channel_name,
                              channel_labels=channel_label,
                              image_description=ac_description,
                              original_metadata= et.tostring(
                                  self._xml, encoding='utf8', method='xml'),
                              offset=3)

if __name__ == '__main__':
    import timeit

    tic = timeit.default_timer()
    fn = '/home/anton/Downloads/test/IMMUcan_Batch20191023_10032401-HN-VAR-TIS-01-IMC-01_AC2.mcd'
    with McdParser(fn) as testmcd:
        imc_img = testmcd.get_imc_acquisition("1")
    print(timeit.default_timer() - tic)
