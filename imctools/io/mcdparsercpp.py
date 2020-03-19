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
        self._cppmcd = mcd
        self.retrieve_mcd_xml()
        self.parse_mcd_xml()

    def retrieve_mcd_xml(self):
        meta = self._cppmcd.readMetadata()
        self._cppmeta = meta
        self._xml = et.fromstring(meta.schemaXML)
        self._ns = "{" + self._xml.tag.split("}")[0].strip("{") + "}"

    @property
    def filename(self):
        return self._filename

    def get_acquisition_buffer(self):
        raise NotImplementedError("Returning buffer not implemented for this parser")

    def get_acquisition_rawdata(self, ac_id):
        ac = [ac for ac in self._cppmeta.acquisitions if ac.properties["ID"] == ac_id][
            0
        ]
        acdat = self._cppmcd.readAcquisitionData(ac)
        dat = np.vstack([c.data for c in acdat.channelData]).T
        return dat

    def close(self):
        pass
