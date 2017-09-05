from __future__ import with_statement, division
import xml.etree.ElementTree as et
from xml.dom import minidom
import struct
import array
import sys
import re
import os
from imctools.io.imcacquisitionbase import ImcAcquisitionBase
from imctools.io.abstractparserbase import AbstractParserBase
from imctools.io.mcdxmlparser import McdXmlParser
import imctools.io.mcdxmlparser as mcdmeta
from imctools.io.abstractparserbase import AcquisitionError

from collections import defaultdict

"""
Main class
"""

class McdParserBase(AbstractParserBase):
    """Parsing data from Fluidigm MCD files

    The McdParser object should be closed using the close
    :param object:
    :return:
    """

    def __init__(self, filename, filehandle = None):
        """

        :param filename:
        """
        AbstractParserBase.__init__(self)

        if filehandle is None:
            self._fh = open(filename, mode='rb')
        else:
            self._fh = filehandle
        self._xml = None
        self._ns = None
        self._acquisition_dict = None
        self.retrieve_mcd_xml()
        self.parse_mcd_xml()

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
        return len(self.meta.get_acquisitions())

    @property
    def acquisition_ids(self):
        """
        Acquisition IDs
        :return:
        """
        return list(self.meta.get_acquisitions().keys())

    def get_acquisition_description(self, ac_id, default=None):
        """
        Get the description field of the acquisition
        :param ac_id:
        :return:
        """
        acmeta = self.meta.get_acquisition_meta(ac_id)
        desc = acmeta.get(mcdmeta.DESCRIPTION, default)
        return desc

    def get_acquisition_buffer(self, ac_id):
        """
        Returns the raw buffer for the acquisition
        :param ac_id: the acquisition id
        :return: the acquisition buffer
        """
        f = self._fh
        ac = self.meta.get_acquisitions()[ac_id]
        data_offset_start = ac.data_offset_start
        data_offset_end = ac.data_offset_end
        data_size = ac.data_size
        n_rows = ac.data_nrows
        n_channel = ac.n_channels
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

        ac = self.meta.get_acquisitions()[ac_id]
        data_offset_start = ac.data_offset_start
        data_offset_end = ac.data_offset_end
        data_size = ac.data_size
        n_rows = ac.data_nrows
        n_channel = ac.n_channels
        if n_rows == 0:
            raise AcquisitionError('Acquisition ' + ac_id + ' emtpy!')
        
        f.seek(data_offset_start)
        dat = array.array('f')
        dat.fromfile(f, (n_rows * n_channel))
        if sys.byteorder != 'little':
            dat.byteswap()
        data = [dat[(row * n_channel):((row * n_channel) + n_channel)]
                for row in range(n_rows)]
        return data

    def get_nchannels_acquisition(self, ac_id):
        """
        Get the number of channels in an acquisition
        :param ac_id:
        :return:
        """
        ac = self.meta.get_acquisitions()[ac_id]
        return ac.n_channels

    def get_acquisition_channels(self, ac_id):
        """
        Returns a dict with the channel metadata
        :param ac_id: acquisition ID
        :return: dict with key: channel_nr, value: (channel_name, channel_label)
        """
        ac = self.meta.get_acquisitions()[ac_id]
        channel_dict = ac.get_channel_orderdict()
        return channel_dict

    def parse_mcd_xml(self):
        """
        Parse the mcd xml into a metadata object
        """
        self._meta = McdXmlParser(self.xml)

    @property
    def meta(self):
        return self._meta
        

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
        """
        f = self._fh
        xml_start = self._reverse_find_in_buffer(f, start_str.encode('utf-8'))

        if xml_start == -1:
            start_str = self._add_nullbytes(start_str)
            xml_start = self._reverse_find_in_buffer(f, start_str.encode('utf-8'))

        if xml_start == -1:
            raise ValueError('Invalid MCD: MCD xml start tag not found in file %s' % self.filename)
        else:
            xml_stop = self._reverse_find_in_buffer(f, stop_str.encode('utf-8'))
            if xml_stop == -1:
                stop_str = self._add_nullbytes(stop_str)
                xml_stop = self._reverse_find_in_buffer(f, stop_str.encode('utf-8'))
                # xmls = [mm[start:end] for start, end in zip(xml_starts, xml_stops)]

        if xml_stop == -1:
            raise ValueError('Invalid MCD: MCD xml stop tag not found in file %s' % self.filename)
        else:
            xml_stop += len(stop_str)

        f.seek(xml_start)
        xml = f.read(xml_stop-xml_start).decode('utf-8')
        xml = xml.replace('\x00','')
        #print(xml)
        self._xml = et.fromstring(xml)
        self._ns = '{'+self._xml.tag.split('}')[0].strip('{')+'}'

    def get_imc_acquisition(self, ac_id, ac_description=None):

        data = self.get_acquisition_rawdata(ac_id)
        nchan = self.get_nchannels_acquisition(ac_id)
        channels = self.get_acquisition_channels(ac_id)
        channel_name, channel_label = zip(*[channels[i] for i in range(nchan)])

        img = self._reshape_long_2_cyx(data, is_sorted=True)

        if ac_description is None:
           ac_description = self.meta.get_object(mcdmeta.ACQUISITION, ac_id).metaname

        return ImcAcquisitionBase(image_ID=ac_id,
                                  original_file=self.filename,
                                  data=img,
                                  channel_metal=channel_name,
                                  channel_labels=channel_label,
                                  original_metadata=str(
                                                     et.tostring(self._xml)),
                                  image_description=ac_description,
                                  origin='mcd',
                                  offset=3)

    def save_panorama(self, pid, out_folder, fn_out=None):
        """
        Save all the panorma images of the acquisition
        :param out_folder: the output folder
        """
        pano_postfix = 'pano'
        image_offestfix = 161
        p = self.meta.get_object(mcdmeta.PANORAMA, pid)
        img_start = int(p.properties[mcdmeta.IMAGESTARTOFFSET]) + image_offestfix
        img_end = int(p.properties[mcdmeta.IMAGEENDOFFSET]) + image_offestfix

        if img_start-img_end == 0:
            pass

        file_end = '.'+p.properties.get(mcdmeta.IMAGEFORMAT, 'png').lower()

        if fn_out is None:
            fn_out = p.metaname

        if not(fn_out.endswith(file_end)):
            fn_out += '_'+pano_postfix+'.' + file_end

        buf = self._get_buffer(img_start, img_end)
        with open(os.path.join(out_folder, fn_out), 'wb') as f:
            f.write(buf)

    def save_slideimage(self, sid, out_folder, fn_out=None):
        image_offestfix = 161
        slide_postfix = 'slide'
        slide_format = '.png'

        s = self.meta.get_object(mcdmeta.SLIDE, sid)
        img_start = int(s.properties[mcdmeta.IMAGESTARTOFFSET]) + image_offestfix
        img_end = int(s.properties[mcdmeta.IMAGEENDOFFSET]) + image_offestfix

        if img_start-img_end == 0:
            pass

        if fn_out is None:
            fn_out = s.metaname
        if not(fn_out.endswith(slide_format)):
            fn_out += '_'+slide_postfix+slide_format

        buf = self._get_buffer(img_start, img_end)
        with open(os.path.join(out_folder, fn_out), 'wb') as f:
            f.write(buf)


    def save_acquisition_bfimage_before(self, ac_id, out_folder, fn_out=None):
        ac_postfix = 'before'
        start_offkey = mcdmeta.BEFOREABLATIONIMAGESTARTOFFSET
        end_offkey = mcdmeta.BEFOREABLATIONIMAGEENDOFFSET

        self._save_acquisition_bfimage(ac_id, out_folder, ac_postfix,
                                       start_offkey, end_offkey, fn_out)
        
    def save_acquisition_bfimage_after(self, ac_id, out_folder, fn_out=None):
        ac_postfix = 'after'
        start_offkey = mcdmeta.AFTERABLATIONIMAGESTARTOFFSET
        end_offkey = mcdmeta.AFTERABLATIONIMAGEENDOFFSET

        self._save_acquisition_bfimage(ac_id, out_folder, ac_postfix,
                                       start_offkey, end_offkey, fn_out)

    def _save_acquisition_bfimage(self, ac_id, out_folder,
                                 ac_postfix, start_offkey, end_offkey, fn_out=None):
        image_offestfix = 161
        image_format = '.png'
        a = self.meta.get_object(mcdmeta.ACQUISITION, ac_id)
        img_start = int(a.properties[start_offkey]) + image_offestfix
        img_end = int(a.properties[end_offkey]) + image_offestfix
        if img_end-img_start == 0:
            pass

        if fn_out is None:
            fn_out = a.metaname
        buf = self._get_buffer(img_start, img_end)
        if not(fn_out.endswith(image_format)):
            fn_out += '_'+ac_postfix+ image_format
            
        with open(os.path.join(out_folder, fn_out), 'wb') as f:
            f.write(buf)

    def save_meta_xml(self, out_folder):
        self.meta.save_meta_xml(out_folder)

    def get_all_imcacquistions(self):
        """
        Returns a list of all nonempty imc_acquisitions
        """
        imc_acs = list()
        for ac in self.acquisition_ids:
            try:
                imcac = self.get_imc_acquisition(ac)
            except AcquisitionError:
                pass
            imc_acs.append(imcac)
        return imc_acs

    def _get_buffer(self, start, stop):
        f = self._fh
        f.seek(start)
        buf = f.read(stop-start)
        return buf


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

        >>> McdParserBase._add_nullbytes('abc')
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
        cur_pos = f.tell() - bsize+1
        f.seek(cur_pos)
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
