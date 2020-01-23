import xml.etree.ElementTree as ET

import tifffile
import xmltodict

from imctools.data import Acquisition


class OmeTiffParser:
    """Data parsing from OME-TIFF files

    """

    origin = "ome.tiff"

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data, self.ome = OmeTiffParser._read_file(filepath)
        self.metadata = self.parse_ome_metadata(self.ome)

    def get_imc_acquisition(self):
        """
        Get Imc Acquisition object

        :return:
        """
        meta = self.metadata
        return Acquisition(meta['image_ID'],
                              self.original_file,
                              self.data,
                              meta['channel_metals'],
                              meta['channel_labels'],
                              original_metadata=self.ome ,
                              image_description=None,
                              origin=self.origin,
                              offset=0)

    def parse_ome_metadata(self, xml: str):
        d = xmltodict.parse(
            xml,
            process_namespaces=False,
            xml_attribs=True,
        )

        result = {
            # 'image_ID': d.get(),
            # 'channel_names': [chan_dict[i][1] for i in range(nchan)],
            # 'channel_labels': [chan_dict[i][0] for i in range(nchan)]
        }
        return result

        # xml = self.ome
        # ns = self.ns
        # img = xml.find(ns+'Image')
        # pixels = img.find(ns+'Pixels')
        # channels = pixels.findall(ns+'Channel')
        # nchan = len(channels)
        # chan_dict={int(chan.attrib['ID'].split(':')[2]) :
        #                (chan.attrib['Name'], chan.attrib['Fluor']) for chan in channels}
        #
        # meta_dict.update({'image_ID': img.attrib['Name'],
        #                   'channel_names': [chan_dict[i][1] for i in range(nchan)],
        #                   'channel_labels': [chan_dict[i][0] for i in range(nchan)]})

    @staticmethod
    def _read_file(filepath: str):
        with tifffile.TiffFile(filepath) as tif:
            data = tif.asarray(out="memmap")
            try:
                ome = tif.pages[0].tags['ImageDescription'].value
            except:
                ome = tif.pages[0].tags['image_description'].value
            return data, ome


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()
    filename = "/home/anton/Downloads/test_2x.ome.tiff"
    parser = OmeTiffParser(filename)
    print(timeit.default_timer() - tic)
