import xml.etree as et
import imctools.librarybase as libb

"""
This module should help parsing the MCD xml metadata
"""

ABLATIONDISTANCEBETWEENSHOTSX = 'AblationDistanceBetweenShotsX'
ABLATIONDISTANCEBETWEENSHOTSY = 'AblationDistanceBetweenShotsY'
ABLATIONFREQUENCY = 'AblationFrequency'
ABLATIONPOWER = 'AblationPower'
ACQUISITION = 'Acquisition'
ACQUISITIONCHANNEL = 'AcquisitionChannel'
ACQUISITIONID = 'AcquisitionID'
ACQUISITIONROI = 'AcquisitionROI'
ACQUISITIONROIID = 'AcquisitionROIID'
AFTERABLATIONIMAGEENDOFFSET = 'AfterAblationImageEndOffset'
AFTERABLATIONIMAGESTARTOFFSET = 'AfterAblationImageStartOffset'
BEFOREABLATIONIMAGEENDOFFSET = 'BeforeAblationImageEndOffset'
BEFOREABLATIONIMAGESTARTOFFSET = 'BeforeAblationImageStartOffset'
CHANNELLABEL = 'ChannelLabel'
CHANNELNAME = 'ChannelName'
DATAENDOFFSET = 'DataEndOffset'
DATASTARTOFFSET = 'DataStartOffset'
DESCRIPTION = 'Description'
DUALCOUNTSTART = 'DualCountStart'
ENDTIMESTAMP = 'EndTimeStamp'
FILENAME = 'Filename'
HEIGHTUM = 'HeightUm'
ID = 'ID'
IMAGEENDOFFSET = 'ImageEndOffset'
IMAGEFILE = 'ImageFile'
IMAGEFORMAT = 'ImageFormat'
IMAGESTARTOFFSET = 'ImageStartOffset'
MCDSCHEMA = 'MCDSchema'
MAXX = 'MaxX'
MAXY = 'MaxY'
MOVEMENTTYPE = 'MovementType'
ORDERNUMBER = 'OrderNumber'
PANORAMA = 'Panorama'
PANORAMAID = 'PanoramaID'
PANORAMAPIXELXPOS = 'PanoramaPixelXPos'
PANORAMAPIXELYPOS = 'PanoramaPixelYPos'
PIXELHEIGHT = 'PixelHeight'
PIXELSCALECOEF = 'PixelScaleCoef'
PIXELWIDTH = 'PixelWidth'
PLUMEEND = 'PlumeEnd'
PLUMESTART = 'PlumeStart'
ROIENDXPOSUM = 'ROIEndXPosUm'
ROIENDYPOSUM = 'ROIEndYPosUm'
ROIPOINT = 'ROIPoint'
ROISTARTXPOSUM = 'ROIStartXPosUm'
ROISTARTYPOSUM = 'ROIStartYPosUm'
ROITYPE = 'ROIType'
SEGMENTDATAFORMAT = 'SegmentDataFormat'
SIGNALTYPE = 'SignalType'
SLIDE = 'Slide'
SLIDEID = 'SlideID'
SLIDETYPE = 'SlideType'
SLIDEX1POSUM = 'SlideX1PosUm'
SLIDEX2POSUM = 'SlideX2PosUm'
SLIDEX3POSUM = 'SlideX3PosUm'
SLIDEX4POSUM = 'SlideX4PosUm'
SLIDEXPOSUM = 'SlideXPosUm'
SLIDEY1POSUM = 'SlideY1PosUm'
SLIDEY2POSUM = 'SlideY2PosUm'
SLIDEY3POSUM = 'SlideY3PosUm'
SLIDEY4POSUM = 'SlideY4PosUm'
SLIDEYPOSUM = 'SlideYPosUm'
STARTTIMESTAMP = 'StartTimeStamp'
TEMPLATE = 'Template'
UID = 'UID'
VALUEBYTES = 'ValueBytes'
WIDTHUM = 'WidthUm'

PARSER = 'parser'


class Meta(object):
    def __init__(self, mtype, meta, parents):
        self.mtype = mtype
        self.id = meta.get(ID, None)
        self.childs = dict()

        self.meta = meta
        self.parents = parents
        for p in parents:
            self._update_parents(p)
        
        self.is_root = len(parents) == 0

        if self.is_root:
            self.objects = dict()
        else:
            # update the root objects
            root = self.get_root()
            self._update_dict(root.objects)
    
    def _update_parents(self, p):
        self._update_dict(p.childs)

    def _update_dict(self, d):
        mtype = self.mtype
        mdict = d.get(mtype, None)
        if mdict is None:
            mdict = dict()
            d[mtype] = mdict
        mdict.update({self.id: self})

    def get_root(self):
        if self.is_root:
            return self
        else:
            return self.parents[0].get_root()


class Slide(Meta):
    def __init__(self, meta, parents):
        super().__init__(SLIDE, meta, parents)

class Panorama(Meta):
    def __init__(self, meta, parents):
        super().__init__(PANORAMA, meta, parents)

class AcquisitionRoi(Meta):
    def __init__(self, meta, parents):
        super().__init__(ACQUISITIONROI, meta, parents)
        
class RoiPoint(Meta):
    def __init__(self, meta, parents):
        super().__init__(ROIPOINT, meta, parents)

class Channel(Meta):
    def __init__(self, meta, parents):
        super().__init__(ACQUISITIONCHANNEL, meta, parents)

class Acquisition(Meta):
    def __init__(self, meta, parents):
        super().__init__(ACQUISITION, meta, parents)


class mcdxmlparser(Meta):
    """
    Represents the full mcd xml
    """
    def __init__(self, xml):
        self._rawxml = xml
        meta = libb.etree_to_dict(xml)
        meta = libb.dict_key_apply(meta, libb.strip_ns)
        meta = meta[MCDSCHEMA]
        
        super().__init__(MCDSCHEMA, meta, [])
        self._init_slides()
        self._init_panoramas()
        self._init_acquisitionroi()
        
    def _init_slides(self):
        """
        gets the slide meta
        """
        slides = self._get_meta_objects(SLIDE)
        for s in slides:
            # slide has only the root as parent
            Slide(s, [self])

    def _init_panoramas(self):
        pano = self._get_meta_objects(PANORAMA)
        for p in pano:
            slideid = p[SLIDEID]
            slide = self.get_object(SLIDE, slideid)
            Panorama(p, [slide])

    def _init_acquisitionroi(self):
        acroi = self._get_meta_objects(ACQUISITIONROI)
        for ar in acroi:
            panoid = ar[PANORAMAID]
            pano = self.get_object(PANORAMA, panoid)
            AcquisitionRoi(ar, [pano])

    def get_object(self, mtype, mid):
        """
        Return an object defined by type and id
        :param mtype: object type
        :param mid: object id
        :returns: the requested object
        """
        return self.objects[mtype][mid]

    def _get_meta_objects(self, mtype):
        """
        A helper to get objects, e.g. slides etc. metadata
        from the metadata dict. takes care of the case where
        only one object is present and thus a dict and not a 
        list of dicts is returned.
        """
        objs = self.meta.get(mtype)
        if isinstance(objs, type(dict())):
            objs = [objs]
        return objs

    def get_channels(self):
        """
        gets a list of all channels
        """
        raise NotImplementedError

    def get_acquisitions(self):
        """
        gets a list of all acquisitions
        """
        raise NotImplementedError

    def get_acquisition_rois(self):
        """
        gets a list of all acuisitionROIs
        """
        raise NotImplementedError

    def get_panoramas(self):
        """
        get a list of all panoramas
        """
        raise NotImplementedError

    def get_roipoints(self):
        """
        get a list of all roipoints
        """
        raise NotImplementedError

