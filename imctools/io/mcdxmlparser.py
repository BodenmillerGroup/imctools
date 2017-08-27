import xml.etree as et
import imctools.librarybase as libb
from collections import OrderedDict

"""
This module should help parsing the MCD xml metadata
"""

# Definition of all the vocabulary used
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

"""
Definition of all the meta objects
Each entity will have a class corresponding to it, with helpermethods
that e.g. allow to retrieve images etc.

This is implemented as parent-child relationships where each entry has a list of parents 
and a nested dictionary of children of the form (child_type: childID: childobject)

Further each object is registered in the global root node, making them easy accessible.
"""
class Meta(object):
    """
    Represents an abstract metadata object.
    """
    def __init__(self, mtype, meta, parents):
        """
        Initializes the metadata object, generates the
        parent-child relationships and updates to object list
        of the root

        :param mtype: the name of the object type
        :param meta: the metadata dictionary
        :param parents:  the parents of this object

        """
        self.mtype = mtype
        self.id = meta.get(ID, None)
        self.childs = dict()

        self.meta = meta
        self.parents = parents
        for p in parents:
            self._update_parents(p)

        if self.is_root:
            self.objects = dict()
        else:
            # update the root objects
            root = self.get_root()
            self._update_dict(root.objects)

    @property
    def is_root(self):
       return len(self.parents) == 0
    
    def _update_parents(self, p):
        self._update_dict(p.childs)

    def _update_dict(self, d):
        mtype = self.mtype
        mdict = d.get(mtype, None)
        if mdict is None:
            mdict = OrderedDict()
            d[mtype] = mdict
        mdict.update({self.id: self})

    def get_root(self):
        """
        Gets the root node of this metadata
        tree
        """
        if self.is_root:
            return self
        else:
            return self.parents[0].get_root()

# Definition of the subclasses
class Slide(Meta):
    def __init__(self, meta, parents):
        super().__init__(SLIDE, meta, parents)

class Panorama(Meta):
    def __init__(self, meta, parents):
        super().__init__(PANORAMA, meta, parents)

class AcquisitionRoi(Meta):
    def __init__(self, meta, parents):
        super().__init__(ACQUISITIONROI, meta, parents)

class Acquisition(Meta):
    def __init__(self, meta, parents):
        super().__init__(ACQUISITION, meta, parents)
        
class RoiPoint(Meta):
    def __init__(self, meta, parents):
        super().__init__(ROIPOINT, meta, parents)

class Channel(Meta):
    def __init__(self, meta, parents):
        super().__init__(ACQUISITIONCHANNEL, meta, parents)


# A dictionary to map metadata keys to metadata types
# The order reflects the dependency structure of them and the
# order these objects should be initialized
OBJ_DICT = OrderedDict([
    (SLIDE, Slide),
    (PANORAMA, Panorama),
    (ACQUISITIONROI, AcquisitionRoi),
    (ACQUISITION, Acquisition),
    (ROIPOINT, RoiPoint),
    (ACQUISITIONCHANNEL, Channel)
])

# A dictionary to map id keys to metadata keys
# Used for initializaiton of the objects
ID_DICT = {
    SLIDEID: SLIDE,
    PANORAMAID: PANORAMA,
    ACQUISITIONROIID: ACQUISITIONROI,
    ACQUISITIONID: ACQUISITION
}

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
        self._init_objects()

    def _init_objects(self):
        obj_keys = [k for k in OBJ_DICT.keys() if k in self.meta.keys()]
        for k in obj_keys:
            ObjClass = OBJ_DICT[k]
            objs = self._get_meta_objects(k)
            idks = [ik for ik in objs[0].keys() if ik in ID_DICT.keys()]
            for o in objs:
                parents = [self.get_objects_by_id(ik, o[ik]) for ik in idks]
                if len(parents) == 0:
                    parents = [self]
                ObjClass(o, parents)
            
    def get_objects_by_id(self, idname, objid):
        """
        Gets objects by idname and id
        :param idname: an name of an id registered in the ID_DICT
        :param objid: the id of the object
        :returns: the described object.
        """
        mtype = ID_DICT[idname]
        return self.get_object(mtype, objid)
        
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

