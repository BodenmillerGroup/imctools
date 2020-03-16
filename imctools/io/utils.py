from typing import Optional, Sequence

import xml.etree.ElementTree as ET

import numpy as np
import xtiff


SESSION_JSON_SUFFIX = "_session.json"
SCHEMA_XML_SUFFIX = "_schema.xml"
OME_TIFF_SUFFIX = "_ac.ome.tiff"
META_CSV_SUFFIX = "_meta.csv"

MCD_FILENDING = ".mcd"
ZIP_FILENDING = ".zip"
CSV_FILENDING = ".csv"
SCHEMA_FILENDING = ".schema"


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


def get_ome_xml(
    img: np.ndarray,
    image_name: Optional[str],
    channel_names: Optional[Sequence[str]],
    big_endian: bool,
    pixel_size: Optional[float],
    pixel_depth: Optional[float],
    creator: Optional[str] = None,
    acquisition_date: Optional[str] = None,
    channel_fluors: Optional[Sequence[str]] = None,
    xml_metadata: Optional[str] = None,
    **ome_xml_kwargs,
) -> ET.ElementTree:
    """Helper function for xtiff library to get a proper OME-TIFF XML"""
    size_t, size_z, size_c, size_y, size_x, size_s = img.shape
    element_tree = xtiff.get_ome_xml(
        img, image_name, channel_names, big_endian, pixel_size, pixel_depth, **ome_xml_kwargs
    )

    if creator is not None:
        ome_element = element_tree.getroot()
        ome_element.set("Creator", creator)

    if acquisition_date is not None:
        image_element = element_tree.find("./Image")
        ET.SubElement(image_element, "AcquisitionDate").text = acquisition_date

    if channel_fluors is not None:
        assert len(channel_fluors) == size_c
        channel_elements = element_tree.findall("./Image/Pixels/Channel")
        assert channel_elements is not None and len(channel_elements) == size_c
        for channel_element, channel_fluor in zip(channel_elements, channel_fluors):
            channel_element.set("Fluor", channel_fluor)

    if xml_metadata is not None:
        ome_element = element_tree.getroot()
        structured_annotations_element = ET.SubElement(ome_element, "StructuredAnnotations")
        xml_annotation_element = ET.SubElement(structured_annotations_element, "XMLAnnotation")
        xml_annotation_element.set("ID", "Annotation:0")
        xml_annotation_value_element = ET.SubElement(xml_annotation_element, "Value")
        original_metadata_element = ET.SubElement(xml_annotation_value_element, "OriginalMetadata")
        ET.SubElement(original_metadata_element, "Key").text = "MCD-XML"
        ET.SubElement(original_metadata_element, "Value").text = xml_metadata.replace("\r\n", "")

    return element_tree
