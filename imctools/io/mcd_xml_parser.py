import csv
import os
from typing import Dict

import xmltodict

from imctools.io.mcd_constants import (
    ACQUISITION,
    ACQUISITION_CHANNEL,
    FILENAME,
    MCD_SCHEMA,
    META_CSV,
    PANORAMA,
    SLIDE,
)
from imctools.io.mcd_xml import ID_DICT, OBJ_DICT, Meta, Acquisition


class McdXmlParser(Meta):
    """Represents the full MCD XML structure

    """

    def __init__(self, xml: str, filename: str = None):
        self._xml = xml
        meta = xmltodict.parse(xml, xml_attribs=False, force_list=(SLIDE, PANORAMA, ACQUISITION, ACQUISITION_CHANNEL))[
            MCD_SCHEMA
        ]
        Meta.__init__(self, MCD_SCHEMA, meta, [])
        if filename is None:
            filename = meta[SLIDE][0][FILENAME]
        self.filename = filename
        self._init_objects()

    @property
    def metaname(self):
        metaname = self.filename
        metaname = metaname.replace("\\", "/")
        metaname = os.path.split(metaname)[1].rstrip("_schema.xml")
        metaname = os.path.splitext(metaname)[0]
        return metaname

    def _init_objects(self):
        obj_keys = [k for k in OBJ_DICT.keys() if k in self.properties.keys()]
        for k in obj_keys:
            ObjClass = OBJ_DICT[k]
            objs = self.properties.get(k)
            idks = [ik for ik in objs[0].keys() if ik in ID_DICT.keys()]
            for o in objs:
                parents = [self.get_objects_by_id(ik, o[ik]) for ik in idks]
                if len(parents) == 0:
                    parents = [self]
                ObjClass(o, parents)

    def get_objects_by_id(self, id_name: str, original_id: str):
        """Gets objects by id name and original object id

        Parameters
        ----------
        id_name
            Name of an id registered in the ID_DICT
        original_id
            Original object id

        """
        meta_type = ID_DICT[id_name]
        return self.get_object(meta_type, original_id)

    def get_object(self, meta_type: str, original_id: str):
        """Return an object defined by type and id

        """
        return self.objects[meta_type][original_id]

    def save_meta_xml(self, out_folder: str):
        filename = self.metaname + "_schema.xml"
        with open(os.path.join(out_folder, filename), "wt") as f:
            f.write(self._xml)

    def save_meta_csv(self, out_folder: str):
        """
        Writes the xml data as csv tables
        """
        for n, o in self.objects.items():
            odict = [i.properties for k, i in o.items()]
            filename = f"{self.metaname}_{n}{META_CSV}"
            with open(os.path.join(out_folder, filename), "wt") as f:
                cols = odict[0].keys()
                writer = csv.DictWriter(f, sorted(cols))
                writer.writeheader()
                for row in odict:
                    writer.writerow(row)

    def get_acquisitions(self) -> Dict[str, Acquisition]:
        """Gets list of all acquisitions

        """
        return self.objects[ACQUISITION]

    def get_acquisition_meta(self, acquisition_id: str):
        """Returns the acquisition metadata dict

        """
        return self.get_object(ACQUISITION, acquisition_id).properties
