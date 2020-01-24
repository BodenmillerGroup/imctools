import os
import uuid
from datetime import datetime

import xmltodict

import imctools.io.mcd.constants as const
from imctools import __version__
from imctools.data import Acquisition, Channel, Panorama, Session, Slide
from imctools.io.parserbase import ParserBase


class McdXmlParser(ParserBase):
    """Represents the full MCD XML structure

    """

    def __init__(self, xml_metadata: str, origin_path: str):
        ParserBase.__init__(self)
        self.xml_metadata = xml_metadata
        self.metadata = xmltodict.parse(
            xml_metadata,
            xml_attribs=False,
            force_list=(
                const.SLIDE,
                const.PANORAMA,
                const.ACQUISITION,
                const.ACQUISITION_CHANNEL,
                const.ACQUISITION_ROI,
            ),
        )[const.MCD_SCHEMA]

        session_name = self.metadata[const.SLIDE][0][const.FILENAME]
        session_name = session_name.replace("\\", "/")
        session_name = os.path.split(session_name)[1].rstrip("_schema.xml")
        session_name = os.path.splitext(session_name)[0]

        session_id = str(uuid.uuid4())
        session = Session(
            session_id,
            session_name,
            __version__,
            self.origin,
            origin_path,
            datetime.utcnow().isoformat(),
            self.metadata,
        )
        for s in self.metadata.get(const.SLIDE):
            slide = Slide(
                session.id,
                int(s.get(const.ID)),
                s.get(const.WIDTH_UM),
                s.get(const.HEIGHT_UM),
                s.get(const.DESCRIPTION),
                metadata=s,
            )
            slide.session = session
            session.slides[slide.id] = slide

        for p in self.metadata.get(const.PANORAMA):
            width = abs(float(p.get(const.SLIDE_X3_POS_UM)) - float(p.get(const.SLIDE_X1_POS_UM)))
            height = abs(float(p.get(const.SLIDE_Y3_POS_UM)) - float(p.get(const.SLIDE_Y1_POS_UM)))
            panorama = Panorama(
                int(p.get(const.SLIDE_ID)),
                int(p.get(const.ID)),
                p.get(const.TYPE),
                p.get(const.DESCRIPTION),
                float(p.get(const.SLIDE_X1_POS_UM)),
                float(p.get(const.SLIDE_Y1_POS_UM)),
                width,
                height,
                float(p.get(const.ROTATION_ANGLE)),
                metadata=p,
            )
            slide = session.slides.get(panorama.slide_id)
            panorama.slide = slide
            slide.panoramas[panorama.id] = panorama
            session.panoramas[panorama.id] = panorama

        rois = dict()
        for r in self.metadata.get(const.ACQUISITION_ROI):
            rois[int(r.get(const.ID))] = r

        for a in self.metadata.get(const.ACQUISITION):
            roi = rois.get(int(a.get(const.ACQUISITION_ROI_ID)))
            panorama = session.panoramas.get(int(roi.get(const.PANORAMA_ID)))
            slide_id = panorama.slide_id
            acquisition = Acquisition(
                slide_id,
                int(a.get(const.ID)),
                a.get(const.MAX_X),
                a.get(const.MAX_Y),
                a.get(const.SIGNAL_TYPE),
                a.get(const.SEGMENT_DATA_FORMAT),
                metadata=a,
            )
            slide = session.slides.get(acquisition.slide_id)
            acquisition.slide = slide
            slide.acquisitions[acquisition.id] = acquisition
            session.acquisitions[acquisition.id] = acquisition

        for c in self.metadata.get(const.ACQUISITION_CHANNEL):
            channel = Channel(
                int(c.get(const.ACQUISITION_ID)),
                int(c.get(const.ID)),
                int(c.get(const.ORDER_NUMBER)),
                c.get(const.CHANNEL_NAME),
                c.get(const.CHANNEL_LABEL),
                metadata=c,
            )
            session.channels[channel.id] = channel
            ac = session.acquisitions.get(channel.acquisition_id)
            channel.acquisition = ac
            ac.channels[channel.id] = channel

        self._session = session

    @property
    def origin(self):
        return "mcd"

    @property
    def session(self):
        return self._session

    def save_meta_xml(self, out_folder: str):
        filename = self.session.name + "_schema.xml"
        with open(os.path.join(out_folder, filename), "wt") as f:
            f.write(self.xml_metadata)
