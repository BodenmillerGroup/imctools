import mcdpy
import numpy as np


import xml.etree.ElementTree as et

from imctools.io.mcdparser import McdParser
from imctools.io.imcacquisition import ImcAcquisition
from imctools.io.abstractparser import AbstractParser

class McdParserCpp(McdParser):
    """
    An mcdparser that uses the bindings to the 
    cpp mcd parsing library (https://github.com/BodenmillerGroup/mcdlib)
    """

    def __init__(self, filename):
        """
        :param filename: the filename of the mcd file

        :returns: the mcd parser object
        """
        self._filename = filename
        mcd = mcdpy.MCDFile(filename)
        self._mcd = mcd
        self.retrieve_mcd_xml()
        self.get_mcd_data()

    def get_mcd_data(self):
        ac_dict = {ac.properties['ID']: ac
         for ac in self._meta.acquisitions}
        self._acquisition_dict = ac_dict
    
    def retrieve_mcd_xml(self):
        meta = self._mcd.readMetadata()
        self._meta = meta
        self._xml = et.fromstring(meta.schemaXML)
        self._ns = '{'+self._xml.tag.split('}')[0].strip('{')+'}'

    @property
    def filename(self):
        return self._filename

    def get_acquisition_buffer(self):
        raise NotImplementedError('Returning buffer not implemented for this parser')

    def get_acquisition_rawdata(self, ac_id):
        ac_dict = self._acquisition_dict
        ac = ac_dict[ac_id]
        acdat = self._mcd.readAcquisitionData(ac)
        dat = np.vstack([c.data for c in acdat.channelData]).T
        return dat

    def get_nchannels_acquisition(self, acid):
        acdat = self._acquisition_dict(acid)
        return len(acdat.channels)
