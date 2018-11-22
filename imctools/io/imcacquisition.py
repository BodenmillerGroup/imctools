"""
This defines the IMC acquisition base class
"""
import os

try:
    import numpy as np
    _have_numpy = True
except ImportError as ix:
    _have_numpy = False

import xml.etree.ElementTree as et

from imctools.io.tiffwriter import TiffWriter
from imctools.io.imcacquisitionbase import ImcAcquisitionBase


class ImcAcquisition(object):
    """
     An Image Acquisition Object representing a single acquisition

    """

    def __init__(self, image_ID, original_file, data, channel_metal, channel_labels,
                 original_metadata=None, image_description=None, origin=None, offset=0):
        """

        :param image_ID: The acquisition ID
        :param original_file: The original filepath
        :param data: the image data
        :param channel_metal: the channel name (metal)
        :param channel_labels: the channel label (meaningful label)
        :param original_metadata: the original metadata, e.g. an MCDPublic XML
        :param image_description: the image description. For MCD acquisitions this is the
                                 metadata based name.

        """
        self.image_ID = image_ID
        self.original_file = original_file

        self._data = data

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

    def get_img_stack_cyx(self, channel_idxs=None, offset=None):
        """
        Return the data reshaped as a stack of images
        :param: channel_idxs
        :return:
        """
        if offset is None:
            offset = self._offset
        if channel_idxs is None:
            channel_idxs = range(self.n_channels)

        data = self._data

        img = [data[i+offset] for i in channel_idxs]

        return img


    def get_img_by_channel_nr(self, chan):
        """

        :param chan:
        :return:
        """
        img = self.get_img_stack_cyx(channel_idxs=[chan])
        return img[0]

    def get_img_by_metal(self, metal):
        chan = self._get_position(metal, self.channel_metals)
        return self.get_img_by_channel_nr(chan)

    def get_img_by_label(self, label):
        chan = self._get_position(label, self.channel_labels)
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

            for i in range(self._offset):
                if i < 3:
                    channel = ['X', 'Y', 'Z'][i] + channel
                else:
                    channel = [str(i)] + channel

        elif len(channel) == self.n_channels + self._offset:
            pass
        else:
            raise ValueError('Incompatible channel names/labels!')

        # remove special characters
        channel = [c.replace('(','').replace(')','').strip() if c is not None else '' for c in channel]
        return channel


    @staticmethod
    def _get_position(name, namelist):
        pos = [i for i, chan in enumerate(namelist) if chan ==name]
        return pos[0]

    def save_image(self, filename, metals=None, mass=None):
        tw = self.get_image_writer(filename, metals=metals, mass=mass)
        tw.save_image()

    def get_image_writer(self, filename, metals=None, mass=None):
        """
        Get an image writer with the right data
        :param filename:
        :param metals:
        :return:
        """

        if not _have_numpy:
            raise NotImplementedError("missing case where numpy not installed")

        if metals is not None:
            order = self.get_metal_indices(metals)

        elif mass is not None:
            order = self.get_mass_indices(mass)
        else:
            order = [i for i in range(self.n_channels)]

        out_names = [self.channel_labels[i] for i in order]
        out_fluor = [self.channel_metals[i] for i in order]
        dat = np.array(self.get_img_stack_cyx(order), dtype=np.float32).swapaxes(2, 0)
        tw = TiffWriter(filename, dat, channel_name=out_names, original_description=self.original_metadata, fluor=out_fluor)
        return tw
