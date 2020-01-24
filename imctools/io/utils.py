from typing import Optional, Sequence

import xml.etree.ElementTree as ET

import numpy as np
import xtiff

_OME_CHANNEL_XML_FMT = '<Channel ID="Channel:0:{id:d}" SamplesPerPixel="{samples_per_pixel:d}"{channel_extra} />'


def reshape_long_2_cyx(
    data: np.memmap,
    is_sorted: bool = True,
    shape: Optional[np.ndarray] = None,
    channel_indices: Optional[Sequence[int]] = None,
):
    """
    Reshape data from long format into cyx format (channels, y, x)

    Parameters
    ----------
    data
        Input data
    is_sorted
        Whether data are sorted
    shape
        Custom data shape
    channel_indices
        Channel indices

    """
    if shape is None:
        shape = data[:, :2].max(axis=0) + 1
        if np.prod(shape) > data.shape[0]:
            shape[1] -= 1
        shape = shape.astype(int)

    if channel_indices is None:
        channel_indices = range(data.shape[1])

    n_channels = len(channel_indices)

    if is_sorted:
        tmp_data = data[:, channel_indices]
        img = np.reshape(tmp_data[: (np.prod(shape)), :], [shape[1], shape[0], n_channels], order="C")
        img = img.swapaxes(0, 2)
        img = img.swapaxes(1, 2)
        return img
    else:
        return NotImplemented


def get_ome_xml(img: np.ndarray, image_name: Optional[str], channel_names: Optional[Sequence[str]], big_endian: bool, pixel_size: Optional[float], pixel_depth: Optional[float], creator: Optional[str] = None,
                   channel_fluors: Optional[Sequence[str]] = None, **ome_xml_kwargs) -> ET.ElementTree:
    size_t, size_z, size_c, size_y, size_x, size_s = img.shape
    element_tree = xtiff.get_ome_xml(img, image_name, channel_names, big_endian, pixel_size, pixel_depth, **ome_xml_kwargs)
    if creator is not None:
        ome_element = element_tree.getroot()
        ome_element.set('Creator', creator)
    if channel_fluors is not None:
        assert len(channel_fluors) == size_c
        channel_elements = element_tree.findall('./Image/Pixels/Channel')
        assert channel_elements is not None and len(channel_elements) == size_c
        for channel_element, channel_fluor in zip(channel_elements, channel_fluors):
            channel_element.set('Fluor', channel_fluor)
    return element_tree
