"""
This defines the IMC acquisition base class
"""
import os
import numpy as np
from tiffwriter import TiffWriter



class ImcAcquisition(object):
    """ An Image Acquisition Object representing a single acquisition

    """
    def __init__(self, image_ID, original_file, data, channel_names, channel_labels,
                 original_metadata = None):
        """

        :param image_ID: The acquisition ID
        :param original_file: The original filepath
        :param data: the image data in a long format, First 3 rows must be X, Y, Z
        :param channel_names: the channel name (metal)
        :param channel_labels: the channel label (meaningful label)
        :param original_metadata: the original metadata, e.g. an MCDPublic XML
        """
        self._image_ID = image_ID
        self._original_file = original_file
        self._data = self._sort_data(data)
        # calculated with update shape
        self._shape = None
        # infered from the xyz
        self._update_shape()

        assert np.prod(self.shape[:-1])*self._data.shape[1] == np.prod(self._data.shape),\
            'Dataset not complete!'

        self._channel_names = self.validate_channels(channel_names)
        self._channel_labels = self.validate_channels(channel_labels)
        self._original_metadata = original_metadata

    @property
    def original_filename(self):
        return os.path.filename(self._image_ID)

    @property
    def n_channels(self):
        return self._data.shape[1]-3

    @property
    def shape(self):
        return self._shape

    @property
    def channel_names(self):
        return self._channel_names[3:]

    @property
    def channel_labels(self):
        return self._channel_labels[3:]

    def get_img_stack(self):
        img = self._data[:,3:].reshape(self.shape, order='c')
        return img

    def get_img_by_channel_nr(self, chan):
        chan = chan+3
        img = self._data[:,chan].reshape((self.shape[0], self.shape[1]), order='c')
        return img

    def get_img_by_name(self, name):
        chan = self._get_position(name, self._channel_names)-3
        return self.get_img_by_channel_nr(chan)

    def get_img_by_label(self, label):
        chan = self._get_position(label, self._channel_labels)-3
        return self.get_img_by_channel_nr(chan)

    def save_image(self, filename):
        out_names = [label+'_'+name for label, name in zip(self.channel_labels, self.channel_names)]
        tw = TiffWriter(filename, self.get_img_stack(), channel_name=out_names, original_description=self._original_metadata)
        tw.save_image()


    @staticmethod
    def _get_position(name, namelist):
        pos = [i for i, chan in enumerate(namelist) if chan ==name]
        return pos[0]

    @staticmethod
    def _sort_data(data):
        return data[np.lexsort((data[:,2], data[:,1], data[:,0])),:]

    def _update_shape(self):
        self._shape = tuple(list(self._data[:, :2].max(axis=0).astype(np.int) + 1) +
                            [self.n_channels])

    def validate_channels(self, channel):
        if len(channel) == self.n_channels:
            channel = ['X', 'Y', 'Z'] + channel
        elif len(channel) != self.n_channels+3:
            raise ValueError('Incompatible channel names/labels!')
        return channel

