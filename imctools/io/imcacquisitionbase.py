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


class ImcAcquisitionBase(object):
    """
     An Image Acquisition Object representing a single acquisition

    """
    def __init__(self, image_ID, original_file, data, channel_names, channel_labels,
                 original_metadata=None, image_description=None, origin=None):
        """

        :param image_ID: The acquisition ID
        :param original_file: The original filepath
        :param data: the image data in a long format, First 3 rows must be X, Y, Z
        :param channel_names: the channel name (metal)
        :param channel_labels: the channel label (meaningful label)
        :param original_metadata: the original metadata, e.g. an MCDPublic XML
        """
        self.image_ID = image_ID
        self.original_file = original_file

        self._data = data
        # calculated with update shape
        self._shape = None
        # infered from the xyz
        self._update_shape()

        #    'Dataset not complete!'

        self._channel_names = self.validate_channels(channel_names)
        self._channel_labels = self.validate_channels(channel_labels)
        self.original_metadata = original_metadata
        self.image_description = image_description
        self.origin = origin

    @property
    def original_filename(self):
        return os.path.split(self.original_file)[1]

    @property
    def n_channels(self):
        return len(self._data[0])-3

    @property
    def shape(self):
        return self._shape

    @property
    def channel_names(self):
        return self._channel_names[3:]

    @property
    def channel_labels(self):
        if self._channel_labels is not None:
            return self._channel_labels[3:]
        else:
            return None

    @property
    def data(self):
        return self._data

    def get_img_stack_cyx(self, channel_idxs=None):
        """
        Return the data reshaped as a stack of images
        :param: channel_idxs
        :return:
        """
        if channel_idxs is None:
            channel_idxs = range(self.shape[2])

        data = self._data
        img = self._initialize_empty_listarray([self.shape[0],
                                                self.shape[1],
                                                len(channel_idxs)])
        # will be c, y, x
        for row in data:
            x = int(row[0])
            y = int(row[1])
            for col, idx in enumerate(channel_idxs):
                img[col][y][x] = row[idx+3]

        return img

    def get_img_stack_cxy(self, channel_idxs=None):
        """
        Return the data reshaped as a stack of images
        :param: channel_idxs
        :return:
        """
        if channel_idxs is None:
            channel_idxs = range(self.shape[2])

        data = self._data
        img = self._initialize_empty_listarray([self.shape[1],
                                                self.shape[0],
                                                len(channel_idxs)])
        # will be c, y, x
        for row in data:
            x = int(row[0])
            y = int(row[1])
            for col, idx in enumerate(channel_idxs):
                img[col][x][y] = row[idx + 3]

        return img

    def get_img_by_channel_nr(self, chan):
        """

        :param chan:
        :return:
        """
        img = self.get_img_stack_cxy(channel_idxs=[chan])

        return img[0]

    def get_img_by_name(self, name):
        chan = self._get_position(name, self._channel_names)-3
        return self.get_img_by_channel_nr(chan)

    def get_img_by_label(self, label):
        chan = self._get_position(label, self._channel_labels)-3
        return self.get_img_by_channel_nr(chan)

    def _update_shape(self):
        data = self._data
        x_max = max([row[0] for row in data])+1
        y_max = max([row[1] for row in data])+1
        self._shape = tuple([int(x_max), int(y_max), self.n_channels])

    def validate_channels(self, channel):
        if channel is None:
            return None
        elif len(channel) == self.n_channels:
            channel = ['X', 'Y', 'Z'] + channel
        elif len(channel) != self.n_channels+3:
            raise ValueError('Incompatible channel names/labels!')
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
    from mcdparserbase import McdParserBase
    import time
    fn = '/mnt/imls-bod/data_vito/grade1.mcd'
    with McdParserBase(fn) as testmcd:
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