#! /usr/bin/env python
"""
Creates the basic parser interface
"""
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
__docformat__ = 'reStructuredText'

from __future__ import with_statement, division
import array

try:
    import numpy as np
    _have_numpy = True
except ImportError as ix:
    _have_numpy = False

class AbstractParserBase(object):
    """

    """
    def __init__(self):
        pass

    def get_imc_acquisition(self):
        pass

    def reshape_long_2_cyx(self, longdat, is_sorted=True, shape=None, channel_idxs=None):
        if _have_numpy:
            return self._reshape_long_2_cyx_with_np(longdat,
                                                    is_sorted,
                                                    shape,
                                                    channel_idxs)
        else:
            return self._reshape_long_2_cyx_without_np(longdat,
                                                       is_sorted,
                                                       shape,
                                                       channel_idxs)

    def _reshape_long_2_cyx_with_np(self, longdat, is_sorted=True, shape=None, channel_idxs=None):
        """
        Helper method to convert to cxy from the long format.
        Mainly used by during import step

        :param longdat:
        :param is_sorted:
        :param shape:
        :param channel_idxs:
        :return:
        """

        if shape is None:
            shape = longdat[:, :2].max(axis=0) + 1
            if np.prod(shape) > longdat.shape[0]:
                shape[1] -= 1

            shape = shape.astype(int)
        if channel_idxs is None:
            channel_idxs = range(longdat.shape[1])
        nchan = len(channel_idxs)
        tdat = longdat[:, channel_idxs]
        if is_sorted:
            img = np.reshape(tdat[:(np.prod(shape)),:], [shape[1], shape[0], nchan], order='C')
            img = img.swapaxes(0,2)
            img = img.swapaxes(1, 2)
            return img

        else:
            # VITO: really ?
            return NotImplemented
    
    def _reshape_long_2_cyx_without_np(self, longdat, is_sorted=True, shape=None, channel_idxs=None):
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
            shape = [0, 0]
            for row in longdat:
                if row[0] > shape[0]:
                    shape[0] = int(row[0])
                if row[1] > shape[1]:
                    shape[1] = int(row[1])
            shape[0] += 1
            shape[1] += 1
            if shape[0]*shape[1] > len(longdat):
                shape[1] -= 1

        if channel_idxs is None:
            channel_idxs = range(len(longdat[0]))

        if is_sorted:
            nchans = len(channel_idxs)
            npixels = shape[0] * shape[1]
            tot_len = npixels * nchans
            imar = array.array('f')

            for i in range(tot_len):
                row = i % npixels
                col = channel_idxs[int(i / npixels)]
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

    def _initialize_empty_listarray(self, shape):
        """
        VITO: describe what this method is supposed to do
        """
        imar = array.array('f')
        for i in range(shape[0] * shape[1] * shape[2]): imar.append(-1.)
        
        img = [[imar[(k * shape[0] * shape[1] + j * shape[0]):(k * shape[0] * shape[1] + j * shape[0] + shape[0])]
                for j in range(shape[1])]
               for k in range(shape[2])]
        return img
