import os
import uuid
from datetime import datetime, timezone

import xmltodict
from dateutil.parser import parse

import imctools.io.mcd.constants as const
from imctools import __version__
from imctools.data import Acquisition, Channel, Panorama, Session, Slide
from imctools.io.parserbase import ParserBase


class McdXmlParser(ParserBase):
    """Converts MCD XML structure into IMC session format."""

    def __init__(self, mcd_xml: str, origin_path: str):
        """
        Parameters
        ----------
        xml_metadata
            Metadata in MCD XML text format
        origin_path
            Path to original input .mcd file
        """
        ParserBase.__init__(self)
        self._mcd_xml = mcd_xml
        self.metadata = xmltodict.parse(
            mcd_xml,
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
            datetime.now(timezone.utc),
            metadata=self.metadata,
        )
        for s in self.metadata.get(const.SLIDE):
            slide = Slide(
                session.id,
                int(s.get(const.ID)),
                description=s.get(const.DESCRIPTION),
                width_um=int(s.get(const.WIDTH_UM)),
                height_um=int(s.get(const.HEIGHT_UM)),
                metadata=dict(s),
            )
            slide.session = session
            session.slides[slide.id] = slide

        for p in self.metadata.get(const.PANORAMA):
            width = abs(float(p.get(const.SLIDE_X3_POS_UM, 0)) - float(p.get(const.SLIDE_X1_POS_UM, 0)))
            height = abs(float(p.get(const.SLIDE_Y3_POS_UM, 0)) - float(p.get(const.SLIDE_Y1_POS_UM, 0)))
            panorama = Panorama(
                int(p.get(const.SLIDE_ID)),
                int(p.get(const.ID)),
                p.get(const.TYPE),
                p.get(const.DESCRIPTION, "Pano"),
                float(p.get(const.SLIDE_X1_POS_UM, 0)),
                float(p.get(const.SLIDE_Y1_POS_UM, 0)),
                width,
                height,
                float(p.get(const.ROTATION_ANGLE, 0)),
                metadata=dict(p),
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

            before_ablation_image_exists = (
                int(a.get(const.BEFORE_ABLATION_IMAGE_END_OFFSET, 0))
                - int(a.get(const.BEFORE_ABLATION_IMAGE_START_OFFSET, 0))
            ) != 0
            after_ablation_image_exists = (
                int(a.get(const.AFTER_ABLATION_IMAGE_END_OFFSET, 0))
                - int(a.get(const.AFTER_ABLATION_IMAGE_START_OFFSET, 0))
            ) != 0

            acquisition = Acquisition(
                slide_id,
                int(a.get(const.ID)),
                int(a.get(const.MAX_X)),
                int(a.get(const.MAX_Y)),
                signal_type=a.get(const.SIGNAL_TYPE, "Dual"),
                segment_data_format=a.get(const.SEGMENT_DATA_FORMAT, "Float"),
                ablation_frequency=float(a.get(const.ABLATION_FREQUENCY, 100)),
                ablation_power=float(a.get(const.ABLATION_POWER, 0)),
                start_timestamp=parse(a.get(const.START_TIME_STAMP, session.created.isoformat())),
                end_timestamp=parse(a.get(const.END_TIME_STAMP, session.created.isoformat())),
                movement_type=a.get(const.MOVEMENT_TYPE, "XRaster"),
                ablation_distance_between_shots_x=float(a.get(const.ABLATION_DISTANCE_BETWEEN_SHOTS_X, 1)),
                ablation_distance_between_shots_y=float(a.get(const.ABLATION_DISTANCE_BETWEEN_SHOTS_Y, 1)),
                template=a.get(const.TEMPLATE, ""),
                roi_start_x_pos_um=float(a.get(const.ROI_START_X_POS_UM, 0)),
                roi_start_y_pos_um=float(a.get(const.ROI_START_Y_POS_UM, 0)),
                roi_end_x_pos_um=float(a.get(const.ROI_END_X_POS_UM, 0)),
                roi_end_y_pos_um=float(a.get(const.ROI_END_Y_POS_UM, 0)),
                description=a.get(const.DESCRIPTION, "ROI"),
                metadata=dict(a),
                before_ablation_image_exists=before_ablation_image_exists,
                after_ablation_image_exists=after_ablation_image_exists,
            )
            slide = session.slides.get(acquisition.slide_id)
            acquisition.slide = slide
            slide.acquisitions[acquisition.id] = acquisition
            session.acquisitions[acquisition.id] = acquisition

        for c in self.metadata.get(const.ACQUISITION_CHANNEL):
            if c.get(const.CHANNEL_NAME) in ("X", "Y", "Z"):
                continue
            channel = Channel(
                int(c.get(const.ACQUISITION_ID)),
                int(c.get(const.ID)),
                int(c.get(const.ORDER_NUMBER)),
                c.get(const.CHANNEL_NAME),
                label=c.get(const.CHANNEL_LABEL),
                metadata=dict(c),
            )
            session.channels[channel.id] = channel
            ac = session.acquisitions.get(channel.acquisition_id)
            channel.acquisition = ac
            ac.channels[channel.id] = channel

        self._session = session

    @property
    def origin(self):
        """Origin of the data"""
        return "mcd"

    @property
    def session(self):
        """Root session data"""
        return self._session

    def get_mcd_xml(self):
        """Original (raw) metadata from MCD file in XML format."""
        return self._mcd_xml
