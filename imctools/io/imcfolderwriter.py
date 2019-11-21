import logging
import os
import imctools.io.mcdxmlparser as mcdmeta
import zipfile

logger = logging.getLogger(__name__)

class ImcFolderWriter(object):
    """ A class to write an imc folder """
    def __init__(self, out_folder, mcddata=None, imcacquisitions=None, mcdmeta=None):
        """
        Initializes an ImcFolderWriter that can be used to write out an imcfolder
        and compress it to zip.
        """
        self.acquisitions = list()
        self.mcd = None
        self.meta = None
        self.out_folder = out_folder
        self.acquisitions = list()

        if mcdmeta is not None:
            self.meta = mcdmeta
        if imcacquisitions is not None:
            self.add_imcacquisitions(imcacquisitions)
            add_ac = False
        else:
            add_ac = True

        if mcddata is not None:
            self.add_mcddata(mcddata, add_acquisitions=add_ac)

        if self.meta is None:
            raise ValueError('At least mcdata or mcdmeta need to be specified!')

    @property
    def foldername(self):
        return self.meta.metaname

    def add_imcacquisitions(self, imcacquisitions, append=False):
        if not append:
            self.acquisitions = list()
        self.acquisitions.extend(imcacquisitions)

    def add_mcddata(self, mcddata, add_acquisitions=True):
        self.mcd = mcddata
        self.meta = mcddata.meta
        if add_acquisitions:
            imcacs = self.mcd.get_all_imcacquistions()
            self.add_imcacquisitions(imcacs)

    def write_imc_folder(self, zipfolder=True, remove_folder=None):
        if remove_folder is None:
            remove_folder = zipfolder

        base_folder = self.out_folder
        foldername = self.foldername
        out_folder = os.path.join(self.out_folder, self.foldername)
        if not(os.path.exists(out_folder)):
            os.makedirs(out_folder)

        for ac in self.acquisitions:
            self._write_acquisition(ac, out_folder)
        if self.meta:
            self.meta.save_meta_xml(out_folder)
            self.meta.save_meta_csv(out_folder)

        if self.mcd:
            slide_ids = self.meta.objects.get(mcdmeta.SLIDE, dict()).keys()
            for sid in slide_ids:
                self.mcd.save_slideimage(sid, out_folder)

            pano_ids = self.meta.objects.get(mcdmeta.PANORAMA, dict()).keys()
            for pid in pano_ids:
                self.mcd.save_panorama(pid, out_folder)

            ac_ids = self.meta.objects.get(mcdmeta.ACQUISITION, dict()).keys()
            for aid in ac_ids:
                self.mcd.save_acquisition_bfimage_after(aid, out_folder)
                self.mcd.save_acquisition_bfimage_before(aid, out_folder)

        if zipfolder:
            with zipfile.ZipFile(os.path.join(base_folder, foldername +'_imc.zip'),
                                 'w', compression=zipfile.ZIP_DEFLATED,
                                 allowZip64=True) as imczip:
                for root, d, files in os.walk(out_folder):
                    for fn in files:
                        imczip.write(os.path.join(root,fn),fn)
                        if remove_folder:
                            os.remove(os.path.join(root,fn))

        if remove_folder:
            os.removedirs(out_folder)

    def _write_acquisition(self, ac, out_folder):
        if 0 in ac.shape:
            logger.error(f"Cannot write acquisition with the shape: {ac.shape}")
            return
        file_end = '_ac.ome.tiff'
        if ac.image_description is None:
            ac_id = ac.image_ID
            fn = self.meta.get_object(mcdmeta.ACQUISITION, ac_id).metaname
        else:
            fn = ac.image_description
        img_writer = ac.get_image_writer(os.path.join(out_folder,
                                                      fn+file_end))
        img_writer.save_image(mode='ome')


    def _find_ac_metaname_from_txt_fn(self, ac):
        raise NotImplementedError

if __name__ == '__main__':
    import imctools.io.mcdparser as mcdp
    #fn_mcd = '/home/vitoz/temp/txtvsmcd/20170805_p60-63_slide6_ac1_vz.mcd'
    #fn_mcd = '/mnt/imls-bod/VitoZ/Spheres/20161130_p25_slide2_ac1/20161130_p25_slide2_ac1.mcd'
    #fn_mcd='/mnt/imls-bod/VitoZ/Spheres/20161005_IS2362_4_site1_ac1/20161005_IS2362_4_site1_ac1.mcd'
    # an example of not functional mcd but working txt
    # fn_mcd = /mnt/imls-bod/DanielS/ACD/IMC\ 2.06/Her2_grade3
    fn_mcd ='/mnt/imls-bod/VitoZ/Spheres/20161018_OCT1_slide4_ac1/20161018_OCT1_slide4_ac1.mcd'
    mcd = mcdp.McdParser(fn_mcd)
    mcd.save_meta_xml('/home/vitoz/temp/')
    ifw = ImcFolderWriter('/home/vitoz/temp/', mcddata=mcd)
    ifw.write_imc_folder()
