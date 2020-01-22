import csv
import os
from datetime import datetime

import xmltodict

from imctools import __version__
from imctools.data import Session, Slide, Acquisition, Panorama, Channel
import imctools.io.mcd.constants as const


class McdXmlParser:
    """Represents the full MCD XML structure

    """

    def __init__(self, xml: str, origin_path: str):
        self.xml = xml
        self.meta = xmltodict.parse(
            xml,
            xml_attribs=False,
            force_list=(
                const.SLIDE,
                const.PANORAMA,
                const.ACQUISITION,
                const.ACQUISITION_CHANNEL,
                const.ACQUISITION_ROI,
            ),
        )[const.MCD_SCHEMA]

        self.filename = self.meta[const.SLIDE][0][const.FILENAME]

        session = Session(self.meta_name, __version__, "mcd", origin_path, datetime.utcnow().isoformat(), self.meta)
        for s in self.meta.get(const.SLIDE):
            slide = Slide(
                session.id,
                s.get(const.ID),
                s.get(const.WIDTH_UM),
                s.get(const.HEIGHT_UM),
                s.get(const.DESCRIPTION),
                meta=s,
            )
            slide.session = session
            session.slides[slide.original_id] = slide

        for p in self.meta.get(const.PANORAMA):
            width = abs(float(p.get(const.SLIDE_X3_POS_UM)) - float(p.get(const.SLIDE_X1_POS_UM)))
            height = abs(float(p.get(const.SLIDE_Y3_POS_UM)) - float(p.get(const.SLIDE_Y1_POS_UM)))
            panorama = Panorama(
                p.get(const.SLIDE_ID),
                p.get(const.ID),
                p.get(const.TYPE),
                p.get(const.DESCRIPTION),
                float(p.get(const.SLIDE_X1_POS_UM)),
                float(p.get(const.SLIDE_Y1_POS_UM)),
                width,
                height,
                float(p.get(const.ROTATION_ANGLE)),
                meta=p,
            )
            slide = session.slides.get(panorama.slide_id)
            panorama.slide = slide
            slide.panoramas[panorama.original_id] = panorama
            session.panoramas[panorama.original_id] = panorama

        rois = dict()
        for r in self.meta.get(const.ACQUISITION_ROI):
            rois[r.get(const.ID)] = r

        for a in self.meta.get(const.ACQUISITION):
            roi = rois.get(a.get(const.ACQUISITION_ROI_ID))
            panorama = session.panoramas.get(roi.get(const.PANORAMA_ID))
            slide_id = panorama.slide_id
            acquisition = Acquisition(
                slide_id,
                a.get(const.ID),
                a.get(const.MAX_X),
                a.get(const.MAX_Y),
                a.get(const.SIGNAL_TYPE),
                a.get(const.SEGMENT_DATA_FORMAT),
                meta=a,
            )
            slide = session.slides.get(acquisition.slide_id)
            acquisition.slide = slide
            slide.acquisitions[acquisition.original_id] = acquisition
            session.acquisitions[acquisition.original_id] = acquisition

        for c in self.meta.get(const.ACQUISITION_CHANNEL):
            channel = Channel(
                c.get(const.ACQUISITION_ID),
                c.get(const.ID),
                c.get(const.ORDER_NUMBER),
                c.get(const.CHANNEL_NAME),
                c.get(const.CHANNEL_LABEL),
                meta=c,
            )
            session.channels[channel.original_id] = channel
            ac = session.acquisitions.get(channel.acquisition_id)
            channel.acquisition = ac
            ac.channels[channel.original_id] = channel

        self.session = session

    @property
    def meta_name(self):
        result = self.filename
        result = result.replace("\\", "/")
        result = os.path.split(result)[1].rstrip("_schema.xml")
        result = os.path.splitext(result)[0]
        return result

    def save_meta_xml(self, out_folder: str):
        filename = self.meta_name + "_schema.xml"
        with open(os.path.join(out_folder, filename), "wt") as f:
            f.write(self.xml)

    def save_meta_csv(self, out_folder: str):
        """
        Writes the xml data as csv tables
        """
        for n, o in self.session.items():
            odict = [i.properties for k, i in o.items()]
            filename = f"{self.meta_name}_{n}{const.META_CSV}"
            with open(os.path.join(out_folder, filename), "wt") as f:
                cols = odict[0].keys()
                writer = csv.DictWriter(f, sorted(cols))
                writer.writeheader()
                for row in odict:
                    writer.writerow(row)
