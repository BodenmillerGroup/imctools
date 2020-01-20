from typing import Optional, Sequence

import numpy as np

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


def get_ome_channel_xml(
    img: np.ndarray, channel_id: int, channel_names: Optional[Sequence[str]], channel_fluors: Optional[Sequence[str]]
):
    """
    Function for generating an OME-XML Channel element in the OME-XML header

    Parameters
    ----------
    img
    channel_id
    channel_names
        List of channel labels
    channel_fluors
        List of channel metals

    """
    size_t, size_z, size_c, size_y, size_x, size_s = img.shape
    channel_extra = ""
    if channel_names is not None and channel_names[channel_id]:
        channel_extra += ' Name="{name}"'.format(name=channel_names[channel_id])
    if channel_fluors is not None and channel_fluors[channel_id]:
        channel_extra += ' Fluor="{fluor}"'.format(fluor=channel_fluors[channel_id])
    return _OME_CHANNEL_XML_FMT.format(id=channel_id, samples_per_pixel=size_s, channel_extra=channel_extra)
