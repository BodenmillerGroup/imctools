import os
from typing import BinaryIO
import mmap

import numpy as np

from imctools.io.errors import AcquisitionError
from imctools.io.imc_acquisition import ImcAcquisition
import imctools.io.mcd_constants as const
from imctools.io.mcd_xml_parser import McdXmlParser
from imctools.io.utils import reshape_long_2_cyx


class McdParser:
    """
    Parsing data from Fluidigm MCD files
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
        self._xml = footer[:public_xml_start]
        self._meta = McdXmlParser(self._xml)

    @property
    def filename(self):
        """
        Return the name of the open file
        """
        return self._fh.name

    @property
    def xml(self):
        return self._xml

    @property
    def meta(self):
        return self._meta

    @property
    def n_acquisitions(self):
        """
        Number of acquisitions in the file
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
        desc = acmeta.get(const.DESCRIPTION, default)
        return desc

    def get_acquisition_buffer(self, ac_id):
        """
        Returns the raw buffer for the acquisition
        :param ac_id: the acquisition id
        :return: the acquisition buffer
        """
        ac = self.meta.get_acquisitions()[ac_id]
        self._fh.seek(ac.data_offset_start)
        buffer = self._fh.read(ac.data_size)
        return buffer

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

    def _inject_imc_datafile(self, filename):
        """
        This function is used in cases where the MCD file is corrupted (missing MCD schema)
        but there is a MCD schema file available. In this case the .schema file can
        be loaded with the mcdparser and then the corrupted mcd-data file loaded
        using this function. This will replace the mcd file data in the backend (containing only
        the schema data) with the real mcd file (not containing the mcd xml).
        """
        self.close()
        self._fh = open(filename, mode="rb")

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

    def _get_footer(self, start_str: str = "<MCDSchema", encoding: str = "utf-16-le"):
        with mmap.mmap(self._meta_fh.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            # MCD format documentation recommends searching from end for "<MCDSchema"
            offset = mm.rfind(start_str.encode(encoding))
            if offset == -1:
                raise ValueError(f"'{self.filename}' does not contain MCDSchema XML footer (try different encoding?).")
            mm.seek(offset)
            footer: str = mm.read().decode(encoding)
            return footer

    def get_imc_acquisition(self, ac_id, ac_description=None):
        """
        Returns an ImcAcquisition object corresponding to the ac_id
        :param ac_id: The requested acquisition id
        :returns: an ImcAcquisition object
        """

        data = self.get_acquisition_raw_data(ac_id)
        nchan = data.shape[1]
        channels = self.get_acquisition_channels(ac_id)
        channel_name, channel_label = zip(*[channels[i] for i in range(nchan)])
        img = reshape_long_2_cyx(data, is_sorted=True)
        if ac_description is None:
            ac_description = self.meta.get_object(const.ACQUISITION, ac_id).metaname

        return ImcAcquisition(
            ac_id, self.filename, img, channel_name, channel_label, self.xml, ac_description, "mcd", 3,
        )

    def save_panorama(self, pid, out_folder, fn_out=None):
        """
        Save all the panorma images of the acquisition
        :param out_folder: the output folder
        """
        pano_postfix = "pano"
        image_offestfix = 161
        p = self.meta.get_object(const.PANORAMA, pid)
        img_start = int(p.properties.get(const.IMAGESTARTOFFSET, 0)) + image_offestfix
        img_end = int(p.properties.get(const.IMAGEENDOFFSET, 0)) + image_offestfix

        if img_start - img_end == 0:
            return 0

        file_end = p.properties.get(const.IMAGEFORMAT, ".png").lower()

        if fn_out is None:
            fn_out = p.metaname

        if not (fn_out.endswith(file_end)):
            fn_out += "_" + pano_postfix + "." + file_end

        buf = self._get_buffer(img_start, img_end)
        with open(os.path.join(out_folder, fn_out), "wb") as f:
            f.write(buf)

    def save_slideimage(self, sid, out_folder, fn_out=None):
        image_offestfix = 161
        slide_postfix = "slide"
        default_format = ".png"

        s = self.meta.get_object(const.SLIDE, sid)
        img_start = int(s.properties.get(const.IMAGESTARTOFFSET, 0)) + image_offestfix
        img_end = int(s.properties.get(const.IMAGEENDOFFSET, 0)) + image_offestfix
        slide_format = s.properties.get(const.IMAGEFILE, default_format)
        if slide_format in [None, "", '""', "''"]:
            slide_format = default_format

        slide_format = os.path.splitext(slide_format.lower())
        if slide_format[1] == "":
            slide_format = slide_format[0]
        else:
            slide_format = slide_format[1]

        if img_start - img_end == 0:
            return 0

        if fn_out is None:
            fn_out = s.metaname
        if not (fn_out.endswith(slide_format)):
            fn_out += "_" + slide_postfix + slide_format

        buf = self._get_buffer(img_start, img_end)
        with open(os.path.join(out_folder, fn_out), "wb") as f:
            f.write(buf)

    def save_acquisition_bfimage_before(self, ac_id, out_folder, fn_out=None):
        ac_postfix = "before"
        start_offkey = const.BEFOREABLATIONIMAGESTARTOFFSET
        end_offkey = const.BEFOREABLATIONIMAGEENDOFFSET

        self._save_acquisition_bfimage(ac_id, out_folder, ac_postfix, start_offkey, end_offkey, fn_out)

    def save_acquisition_bfimage_after(self, ac_id, out_folder, fn_out=None):
        ac_postfix = "after"
        start_offkey = const.AFTERABLATIONIMAGESTARTOFFSET
        end_offkey = const.AFTERABLATIONIMAGEENDOFFSET

        self._save_acquisition_bfimage(ac_id, out_folder, ac_postfix, start_offkey, end_offkey, fn_out)

    def _save_acquisition_bfimage(self, ac_id, out_folder, ac_postfix, start_offkey, end_offkey, fn_out=None):
        image_offestfix = 161
        image_format = ".png"
        a = self.meta.get_object(const.ACQUISITION, ac_id)
        img_start = int(a.properties.get(start_offkey, 0)) + image_offestfix
        img_end = int(a.properties.get(end_offkey, 0)) + image_offestfix
        if img_end - img_start == 0:
            return 0

        if fn_out is None:
            fn_out = a.metaname
        buf = self._get_buffer(img_start, img_end)
        if not (fn_out.endswith(image_format)):
            fn_out += "_" + ac_postfix + image_format
        with open(os.path.join(out_folder, fn_out), "wb") as f:
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
                print("error in acqisition: " + ac)
        return imc_acs

    def _get_buffer(self, start: int, stop: int):
        self._fh.seek(start)
        buf = self._fh.read(stop - start)
        return buf

    def close(self):
        """Close file handles"""
        self._fh.close()
        try:
            self._meta_fh.close()
        except:
            pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()
    filename = "/home/anton/Downloads/test/IMMUcan_Batch20191023_10032401-HN-VAR-TIS-01-IMC-01_AC2.mcd"
    # filename = "/home/anton/Data/20170905_Fluidigmworkshopfinal_SEAJa/20170905_Fluidigmworkshopfinal_SEAJa.mcd"
    with McdParser(filename) as mcd:
        imc_img = mcd.get_imc_acquisition("1")
        imc_img.save_image("/home/anton/Downloads/test.ome.tiff")
        pass
    print(timeit.default_timer() - tic)
