from typing import BinaryIO
import mmap

import numpy as np
import xmltodict

from imctools.io.errors import AcquisitionError
from imctools.io.mcd_xml_parser import McdXmlParser

"""
This module should help parsing the MCD xml metadata
"""


class McdParser:
    """Parsing data from Fluidigm MCD files

    The McdParser object should be closed using the close method
    """

    def __init__(self, filename: str, file_handle: BinaryIO = None, meta_filename: str = None):
        """

        Parameters
        ----------

        filename
            Filename of an .mcd file
        file_handle
            File handle pointing to an open .mcd file
        """
        if file_handle is None:
            self._fh = open(filename, mode="rb")
        else:
            self._fh = file_handle

        if meta_filename is None:
            self._meta_fh = self._fh
        else:
            self._meta_fh = open(meta_filename, mode="rb")

        self._acquisition_dict = None

        footer = self._get_footer()
        public_xml_start = footer.find("<MCDPublic")
        self._xml_private = footer[:public_xml_start]
        self._xml_public = footer[public_xml_start:]

        self._meta_private = McdXmlParser(self._xml_private)
        self._meta_public = McdXmlParser(self._xml_public)

    @property
    def filename(self):
        """
        Return the name of the open file
        """
        return self._fh.name

    @property
    def xml_private(self):
        return self._xml_private

    @property
    def xml_public(self):
        return self._xml_public

    @property
    def meta_private(self):
        return self._meta_private

    @property
    def meta_public(self):
        return self._meta_public

    @property
    def n_acquisitions(self):
        """
        Number of acquisitions in the file
        """
        return len(self.meta_private.get_acquisitions())

    @property
    def acquisition_ids(self):
        """
        Acquisition IDs
        :return:
        """
        return list(self.meta.get_acquisitions().keys())

    def parse_mcd_xml(self):
        """
        Parse the mcd xml into a metadata object
        """
        self._meta = McdXmlParser(self.xml)

    def get_acquisition_raw_data(self, acquisition_id: int):
        """
        Gets non-reshaped image data from the acquisition

        Parameters
        ----------
        acquisition_id
            Acquisition ID
        """
        ac = self.meta.get_acquisitions()[acquisition_id]
        data_offset_start = ac.data_offset_start
        data_offset_end = ac.data_offset_end
        data_size = ac.data_size
        n_rows = ac.data_nrows
        n_channel = ac.n_channels

        if n_rows == 0:
            raise AcquisitionError(f"Acquisition {acquisition_id} emtpy!")

        data = np.memmap(self._fh, dtype=np.float32, mode="r", offset=data_offset_start, shape=(int(n_rows), n_channel))
        return data

    def _get_footer(self, start_str: str = "<MCDSchema", encoding: str = "utf-16-le"):
        with mmap.mmap(self._meta_fh.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            # MCD format documentation recommends searching from end for "<MCDSchema"
            offset = mm.rfind(start_str.encode(encoding))
            if offset == -1:
                raise ValueError(f"'{self.filename}' does not contain MCDSchema XML footer (try different encoding?).")
            mm.seek(offset)
            footer: str = mm.read().decode(encoding)
            return footer

    def get_public_schema(self):
        footer = self.get_footer(start_str="<MCDPublic")
        schema = xmltodict.parse(footer, force_list=("Acquisition", "AcquisitionChannel"))["MCDSchema"]
        return schema

    def retrieve_mcd_xml(self, start_str: str = "<MCDSchema", stop_str: str = "</MCDSchema>"):
        """
        Finds the MCD metadata XML in the binary and updates the McdParser object.
        As suggested in the specifications the file is parsed from the end.

        Parameters
        ----------
        start_str
        stop_str
        """
        mm = mmap.mmap(self._meta_fh.fileno(), 0, access=mmap.ACCESS_READ)

        xml_start = mm.rfind(start_str.encode("utf-8"))

        if xml_start == -1:
            start_str = self._add_nullbytes(start_str)
            xml_start = mm.rfind(start_str.encode("utf-8"))

        if xml_start == -1:
            raise ValueError(f"Invalid MCD: MCD xml start tag not found in file {self.filename}")
        else:
            xml_stop = mm.rfind(stop_str.encode("utf-8"))
            if xml_stop == -1:
                stop_str = self._add_nullbytes(stop_str)
                xml_stop = mm.rfind(stop_str.encode("utf-8"))
                # xmls = [mm[start:end] for start, end in zip(xml_starts, xml_stops)]

        if xml_stop == -1:
            raise ValueError("Invalid MCD: MCD xml stop tag not found in file %s" % self.filename)
        else:
            xml_stop += len(stop_str)

        xml = mm[xml_start:xml_stop].decode("utf-8")
        # This is for mcd schemas, where the namespace are often messed up.
        xml = xml.replace("diffgr:", "").replace("msdata:", "")
        self._xml = et.fromstring(xml)
        self._ns = "{" + self._xml.tag.split("}")[0].strip("{") + "}"

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

        return ImcAcquisition(
            image_ID=ac_id,
            original_file=self.filename,
            data=img,
            channel_metal=channel_name,
            channel_labels=channel_label,
            image_description=ac_description,
            original_metadata=et.tostring(self._xml, encoding="utf8", method="xml"),
            offset=3,
        )


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()
    filename = "/home/anton/Downloads/test/IMMUcan_Batch20191023_10032401-HN-VAR-TIS-01-IMC-01_AC2.mcd"
    with McdParser(filename) as mcd:
        imc_img = mcd.get_imc_acquisition("1")
    print(timeit.default_timer() - tic)
