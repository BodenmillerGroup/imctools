#! /usr/bin/env python
# Copyright (C) 2018-2019 University of Zurich. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import with_statement, division

import struct
import array
import sys
import re
import os

try:
    import numpy as np
    _have_numpy = True
except ImportError as ix:
    _have_numpy = False

try:
    import mmap
    _have_mmap = True
except ImportError as ix:
    _have_mmap = False

import xml.etree.ElementTree as et
from xml.dom import minidom

# from imctools.io.mcdparserbase import McdParserBase
from imctools.io.imcacquisition import ImcAcquisition
from imctools.io.abstractparser import AbstractParser
from imctools.io.mcdxmlparser import McdXmlParser
import imctools.io.mcdxmlparser as mcdmeta

import imctools.exceptions

from collections import defaultdict

__docformat__ = 'reStructuredText'


class McdSchema():
    """
    object representing schema file
    """

    def __init__(self, schema_file):
        self.schema_file = schema_file

    def get_xml(self, start_str='<MCDSchema', stop_str='</MCDSchema>'):
        if _have_mmap:
            return self._get_xml_with_mmap(start_str,stop_str)
        else:
            return self._get_xml_without_mmap(start_str,stop_str)


    def _get_xml_without_mmap(self, start_str, stop_str):
        with open(self.schema_file) as f:
            xml_start = self._reverse_find_in_buffer(f, start_str.encode('utf-8'))
            if xml_start:
                start_str = self._add_nullbytes(start_str)
                xml_start = self._reverse_find_in_buffer(f, start_str.encode('utf-8'))

            assert xml_start, "Invalid MCD file {0}: xml start tag not found".format(self.schema_file)

            xml_stop = self._reverse_find_in_buffer(f, stop_str.encode('utf-8'))
            if xml_stop:
                stop_str = self._add_nullbytes(stop_str)
                xml_stop = self._reverse_find_in_buffer(f, stop_str.encode('utf-8'))

            assert xml_stop, "Invalid MCD file {0}: xml stop tag not found".format(self.schema_file)
            xml_stop += len(stop_str)

            f.seek(xml_start)
            xml = f.read(xml_stop-xml_start).decode('utf-8')
            xml = xml.replace('\x00','')
        return et.fromstring(xml)

    def _get_xml_with_mmap(self, start_str, stop_str):
        with open(self.schema_file) as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

            xml_start = mm.rfind(start_str.encode('utf-8'))

            if xml_start:
                start_str = self._add_nullbytes(start_str)
                xml_start = mm.rfind(start_str.encode('utf-8'))
            assert xml_start, "Invalid MCD file {0}: xml start tag not found".format(self.schema_file)

            xml_stop = mm.rfind(stop_str.encode('utf-8'))
            if xml_stop:
                stop_str = self._add_nullbytes(stop_str)
                xml_stop = mm.rfind(stop_str.encode('utf-8'))

            assert xml_stop, "Invalid MCD file {0}: xml stop tag not found".format(self.schema_file)
            xml_stop += len(stop_str)

            xml = mm[xml_start:xml_stop].decode('utf-8')
            # This is for mcd schemas, where the namespace are often messed up.
            xml = xml.replace('diffgr:','').replace('msdata:','')
            return et.fromstring(xml)

    def _add_nullbytes(self, buffer_str):
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


    def _reverse_find_in_buffer(self, f, s, buffer_size=4096):
        # based on http://stackoverflow.com/questions/3893885/cheap-way-to-search-a-large-text-file-for-a-string
        f.seek(0, 2)

        buf = None
        overlap = len(s) - 1
        bsize = buffer_size +overlap+1
        cur_pos = f.tell() - bsize+1
        offset =  (-2*bsize+overlap)
        first_start=True
        while cur_pos >= 0:
            f.seek(cur_pos)
            buf = f.read(bsize)
            if buf:
                pos = buf.find(s)
                if pos >= 0:
                    return f.tell() - (len(buf) - pos)

            cur_pos = f.tell() +offset
            if (cur_pos < 0) and first_start:
                first_start=False
                cur_pos=0
        return None



class McdParser(AbstractParser):
    """Parsing data from Fluidigm MCD files

    The McdParser object should be closed using the close
    :param object:
    :return:
    """
    def __init__(self, filename, filehandle=None, metafilename=None):
        """
        Initializes the MCDparser object
        :param filename: a filename of an .mcd file
        :param filehandle: a filehandle pointing to an open .mcd file
        :returns: the mcdparser object
        """
        AbstractParser.__init__(self)

        if filehandle is None:
            # self._fh = open(filename, mode='rb')
            self._fh = filename
        else:
            self._fh = filehandle

        if metafilename is None:
            self._metafh = self._fh
        else:
            # self._metafh = open(metafilename, mode='rb')
            self._metafh = metafilename

        self.schema = McdSchema(self._metafh)
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
        Gets the unreshaped image data from the acquisition.
        :param ac_id: the acquisition id
        :returns: the acquisition rawdata
        """
        if _have_numpy:
            return self._get_acquisition_rawdata_with_np(ac_id)
        else:
            return self._get_acquisition_rawdata_without_np(ac_id)

    def _get_acquisition_rawdata_with_np(self, ac_id):
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
            raise imctools.exceptions.AcquisitionError('Acquisition ' + ac_id + ' emtpy!')

        data = np.memmap(self._fh, dtype='<f', mode='r',
                             offset=data_offset_start,
                             shape=(int(n_rows), n_channel))
        return data

    def _get_acquisition_rawdata_without_np(self, ac_id):
        """
        Get the acquisition XML of the acquisition with the id
        :param ac_id: the acquisition id
        :return: the acquisition XML
        """
        with open(self._fh, 'rb') as f:
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

    def _inject_imc_datafile(self, filename):
        """
        This function is used in cases where the MCD file is corrupted (missing MCD schema)
        but there is a MCD schema file available. In this case the .schema file can
        be loaded with the mcdparser and then the corrupted mcd-data file loaded
        using this function. This will replace the mcd file data in the backend (containing only
        the schema data) with the real mcd file (not containing the mcd xml).
        """
        self.close()
        self._fh = filename


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
        Finds the MCD metadata XML in the binary  and updates the mcdparser object.
        As suggested in the specifications the file is parsed from the end.

        :param fn:
        :param start_str:
        :param stop_str:
        """
        self._xml = self.schema.get_xml(start_str, stop_str)
        self._ns = '{' + self._xml.tag.split('}')[0].strip('{')+'}'

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

    def save_panorama(self, pid, out_folder, fn_out=None):
        """
        Save all the panorma images of the acquisition
        :param out_folder: the output folder
        """
        pano_postfix = 'pano'
        image_offestfix = 161
        p = self.meta.get_object(mcdmeta.PANORAMA, pid)
        img_start = int(p.properties.get(mcdmeta.IMAGESTARTOFFSET,0)) + image_offestfix
        img_end = int(p.properties.get(mcdmeta.IMAGEENDOFFSET,0)) + image_offestfix

        if img_start-img_end == 0:
            return(0)

        file_end = p.properties.get(mcdmeta.IMAGEFORMAT, '.png').lower()

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
        default_format = '.png'

        s = self.meta.get_object(mcdmeta.SLIDE, sid)
        img_start = int(s.properties.get(mcdmeta.IMAGESTARTOFFSET,0)) + image_offestfix
        img_end = int(s.properties.get(mcdmeta.IMAGEENDOFFSET,0)) + image_offestfix
        slide_format = s.properties.get(mcdmeta.IMAGEFILE, default_format)
        if slide_format is None:
            slide_format = default_format

        slide_format = os.path.splitext(slide_format.lower())
        if slide_format[1] == '':
            slide_format = slide_format[0]
        else:
            slide_format = slide_format[1]

        if img_start-img_end == 0:
            return(0)

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
        img_start = int(a.properties.get(start_offkey,0)) + image_offestfix
        img_end = int(a.properties.get(end_offkey,0)) + image_offestfix
        if img_end-img_start == 0:
            return(0)

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
                imc_acs.append(imcac)
            except AcquisitionError:
                pass
            except:
                print('error in acqisition: '+ac)
        return imc_acs

    def _get_buffer(self, start, stop):
        f = self._fh
        f.seek(start)
        buf = f.read(stop-start)
        return buf


    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

