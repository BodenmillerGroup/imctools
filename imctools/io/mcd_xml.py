"""
Definition of all the meta objects
Each entity will have a class corresponding to it, with helper methods
that e.g. allow to retrieve images etc.

This is implemented as parent-child relationships where each entry has a list of parents
and a nested dictionary of children of the form (child_type: childID: childobject)

Further each object is registered in the global root node, making them easy accessible.

"""
from __future__ import annotations

from collections import OrderedDict
from typing import Dict, Sequence, Optional, Any

import imctools.io.mcd_constants as const


class Meta:
    """
    Represents an abstract metadata object.

    """

    def __init__(self, meta_type: str, properties: Dict[str, str], parents: Sequence[Meta], symbol: Optional[str] = None):
        """
        Initializes the metadata object, generates the
        parent-child relationships and updates to object list
        of the root

        Parameters
        ----------
        properties
            Metadata dictionary
        parents
            Parents of this object
        symbol
            Short symbol for this metadata, e.g. 's' for slide
        """
        self._meta_type = meta_type
        self.properties = properties
        self.parents = parents
        self.symbol = symbol

        self.children: Dict[str, Meta] = dict()

        for p in parents:
            self._update_parents(p)

        if self.is_root:
            self.objects = dict()
        else:
            # update the root objects
            root = self.get_root()
            self._update_dict(root.objects)

    @property
    def meta_type(self):
        return self._meta_type

    @property
    def ID(self):
        return self.properties.get(const.ID)

    @property
    def is_root(self):
        return len(self.parents) == 0

    def _update_parents(self, parent):
        self._update_dict(parent.children)

    def _update_dict(self, d: dict):
        dict_ = d.get(self.meta_type, None)
        if dict_ is None:
            dict_ = dict()
            d[self.meta_type] = dict_
        dict_.update({self.ID: self})

    def get_root(self):
        """
        Gets the root node of the metadata tree
        """
        if self.is_root:
            return self
        else:
            return self.parents[0].get_root()

    @property
    def metaname(self):
        pname = self.parents[0].metaname
        return "_".join([pname, self.symbol + str(self.ID)])


class Slide(Meta):
    def __init__(self, properties, parents):
        Meta.__init__(self, const.SLIDE, properties, parents, "s")


class Panorama(Meta):
    def __init__(self, properties, parents):
        Meta.__init__(self, const.PANORAMA, properties, parents, "p")


class AcquisitionRoi(Meta):
    def __init__(self, properties, parents):
        Meta.__init__(self, const.ACQUISITIONROI, properties, parents, "r")


class Acquisition(Meta):
    def __init__(self, properties, parents):
        Meta.__init__(self, const.ACQUISITION, properties, parents, "a")

    def get_channels(self):
        return self.children[const.ACQUISITIONCHANNEL]

    def get_channel_orderdict(self):
        chan_dic = self.get_channels()
        out_dic = dict()
        for k, chan in chan_dic.items():
            channel_name = chan.properties[const.CHANNELNAME]
            channel_label = chan.properties.get(const.CHANNELLABEL, channel_name)
            channel_order = int(chan.properties.get(const.ORDERNUMBER))
            out_dic.update({channel_order: (channel_name, channel_label)})
        return out_dic

    @property
    def data_offset_start(self):
        return int(self.properties[const.DATASTARTOFFSET])

    @property
    def data_offset_end(self):
        return int(self.properties[const.DATAENDOFFSET])

    @property
    def data_size(self):
        return self.data_offset_end - self.data_offset_start + 1

    @property
    def data_nrows(self):
        nrow = int(self.data_size / (self.n_channels * int(self.properties[const.VALUEBYTES])))
        return nrow

    @property
    def n_channels(self):
        return len(self.get_channels())


class RoiPoint(Meta):
    def __init__(self, properties, parents):
        Meta.__init__(self, const.ROIPOINT, properties, parents, "rp")


class Channel(Meta):
    def __init__(self, properties, parents):
        Meta.__init__(self, const.ACQUISITIONCHANNEL, properties, parents, "c")


"""
A dictionary to map metadata keys to metadata types
The order reflects the dependency structure of them and the order these objects should be initialized
"""
OBJ_DICT = OrderedDict(
    [
        (const.SLIDE, Slide),
        (const.PANORAMA, Panorama),
        (const.ACQUISITIONROI, AcquisitionRoi),
        (const.ACQUISITION, Acquisition),
        (const.ROIPOINT, RoiPoint),
        (const.ACQUISITIONCHANNEL, Channel),
    ]
)

"""
A dictionary to map id keys to metadata keys
Used for initialization of the objects
"""
ID_DICT = {
    const.SLIDEID: const.SLIDE,
    const.PANORAMAID: const.PANORAMA,
    const.ACQUISITIONROIID: const.ACQUISITIONROI,
    const.ACQUISITIONID: const.ACQUISITION,
}
