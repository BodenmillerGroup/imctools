from __future__ import with_statement, division
try:
    xrange
except NameError:
    xrange = range

"""
This defines the IMC acquisition base class
This can be extended too e.g. read the data from a text file instead from a provided array.
"""

import os
import array
import string

class ImcAcquisitionBase(object):
    """
     An Image Acquisition Object representing a single acquisition

    """
    def __init__(self, image_ID, original_file, data, channel_metal, channel_labels,
                 original_metadata=None, image_description=None, origin=None, offset=0, is_long=False, is_sorted=True):
        """

        :param image_ID: The acquisition ID
        :param original_file: The original filepath
        :param data: the image data
        :param channel_metal: the channel name (metal)
        :param channel_labels: the channel label (meaningful label)
        :param original_metadata: the original metadata, e.g. an MCDPublic XML
        """
        self.image_ID = image_ID
        self.original_file = original_file

        if is_long == False:
            self._data = data
        else:
            self._data = self._reshape_long_2_cxy(data,is_sorted=is_sorted)

        self._offset = offset
        # calculated with update shape
        self._shape = None
        # infered from the xyz
        self._update_shape()

        #    'Dataset not complete!'

        self._channel_metals = self.validate_channels(channel_metal)
        self._channel_labels = self.validate_channels(channel_labels)
        self.original_metadata = original_metadata
        self.image_description = image_description
        self.origin = origin


    @property
    def original_filename(self):
        return os.path.split(self.original_file)[1]

    @property
    def n_channels(self):
        return len(self._data)-self._offset

    @property
    def shape(self):
        return self._shape

    @property
    def channel_metals(self):
        return self._channel_metals[self._offset:]

    @property
    def channel_mass(self):
        return [''.join([m for m in metal if m.isdigit()]) for metal in self._channel_metals[self._offset:]]

    @property
    def channel_labels(self):
        if self._channel_labels is not None:
            return self._channel_labels[self._offset:]
        else:
            return None

    def get_metal_indices(self, metallist):
        """
        Returns a list with the indices in the metals from metallist
        :param metallist: List of metal names
        :return:
        """
        order_dict = dict()
        for i, m in enumerate(self.channel_metals):
            order_dict.update({m: i})

        return [order_dict[m] for m in metallist]

    def get_mass_indices(self, masslist):
        """
        Returns the channel indices from the queried mass
        :param masslist:
        :return:
        """

        order_dict = dict()
        for i, m in enumerate(self.channel_mass):
            order_dict.update({m: i})

        return [order_dict[m] for m in masslist]

    @property
    def data(self):
        return self._data

    def get_img_stack_cxy(self, channel_idxs=None, offset=None):
        """
        Return the data reshaped as a stack of images
        :param: channel_idxs
        :return:
        """
        if offset is None:
            offset = self._offset
        if channel_idxs is None:
            channel_idxs = range(self.shape[2])

        data = self._data

        img = [data[i+offset] for i in channel_idxs]

        return img

    @classmethod
    def _reshape_long_2_cxy(self, longdat, is_sorted=True, shape=None, channel_idxs=None):
        """
        Helper method to convert to cxy from the long format.
        Mainly used by during import step
        :param longdat:
        :param is_sorted:
        :param shape:
        :param channel_idxs:
        :param channel_offset:
        :return:
        """
        if shape is None:
            if is_sorted:
                shape = [int(i+1) for i in longdat[-1][:2]]
            else:
                shape = [0,0]
                for row in longdat:
                    if row[0] > shape[0]:
                        row[0] = shape[0]

                    if row[1] > shape[1]:
                        row[1] = shape[1]

        if channel_idxs is None:
            channel_idxs = range(len(longdat[0]))

        if is_sorted:
            nchans = len(channel_idxs)
            npixels = shape[0] * shape[1]
            tot_len = npixels * nchans
            imar = array.array('f')

            for i in xrange(tot_len):
                row = i % npixels
                col = channel_idxs[int(i/npixels)]
                imar.append(longdat[row][col])

            img = [[imar[(k * shape[0] * shape[1] + j * shape[0]):(k * shape[0] * shape[1] + j * shape[0] + shape[0])]
                    for j in range(shape[1])]
                   for k in range(nchans)]

        else:
            img = self._initialize_empty_listarray([shape[1],
                                                        shape[0],
                                                        len(channel_idxs)])
            # will be c, y, x
            for row in longdat:
                x = int(row[0])
                y = int(row[1])
                for col, idx in enumerate(channel_idxs):
                    img[col][x][y] = row[idx]

        return img


    def get_img_by_channel_nr(self, chan):
        """

        :param chan:
        :return:
        """
        img = self.get_img_stack_cxy(channel_idxs=[chan])

        return img[0]

    def get_img_by_metal(self, metal):
        chan = self._get_position(metal, self._channel_metals)
        return self.get_img_by_channel_nr(chan)

    def get_img_by_label(self, label):
        chan = self._get_position(label, self._channel_labels)
        return self.get_img_by_channel_nr(chan)

    def _update_shape(self):
        data = self._data
        x_max = len(data[0])
        y_max = len(data[0][0])
        self._shape = tuple([int(x_max), int(y_max), self.n_channels])

    def validate_channels(self, channel):
        if channel is None:
            return None
        elif len(channel) == self.n_channels:
            channel = ['X', 'Y', 'Z'] + channel
        elif len(channel) == self.n_channels + self._offset:
            pass
        else:
            raise ValueError('Incompatible channel names/labels!')

        # remove special characters
        channel = [c.strip('(').strip(')').strip() for c in channel]
        return channel

    @staticmethod
    def _initialize_empty_listarray(shape):
        imar = array.array('f')
        for i in xrange(shape[0]*shape[1]*shape[2]): imar.append(-1.)

        img = [[imar[(k*shape[0]*shape[1]+j*shape[0]):(k*shape[0]*shape[1]+j*shape[0]+shape[0])]
                for j in range(shape[1])]
               for k in range(shape[2])]

        return img

    @staticmethod
    def _get_position(name, namelist):
        pos = [i for i, chan in enumerate(namelist) if chan ==name]
        return pos[0]

if __name__ == '__main__':
    from mcdparserbase import McdParserBaseBase
    import time
    fn = '/mnt/imls-bod/data_vito/grade1.mcd'
    with McdParserBaseBase(fn) as testmcd:
        print(testmcd.filename)
        print(testmcd.n_acquisitions)
        # print(testmcd.get_acquisition_xml('0'))
        print(testmcd.get_acquisition_channels_xml('0'))
        print(testmcd.get_acquisition_channels('0'))
        print(len(testmcd.get_acquisition_rawdata('0')))

        start = time.time()
        imc_ac = testmcd.get_imc_acquisition('0')
        end = time.time()
        print(end - start)
        print(imc_ac.shape)
        #imc_img.save_image('/mnt/imls-bod/data_vito/test1.tiff')
        # acquisition_dict = get_mcd_data(fn, xml_public)