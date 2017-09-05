import shutil
import os
import imctools.io.mcdxmlparser as mcdmeta

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

    def write_imc_folder(self):
        out_folder = self.out_folder
        for ac in self.acquisitions:
            self._write_acquisition(ac, out_folder)
        if self.meta:
            self.meta.save_meta_xml(out_folder)

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

    def _write_acquisition(self, ac, out_folder):
        file_end = '.ome.tiff'
        if ac.image_description is None:
            fn = ac.original_filename
            fn = os.path.basename(fn)
            fn = os.path.splitext(fn)[0]
        else:
            fn = ac.image_description
        img_writer = ac.get_image_writer(os.path.join(out_folder,
                                                      fn+file_end))
        img_writer.save_image(mode='ome')


    def _find_ac_metaname_from_txt_fn(self, ac):
        raise NotImplementedError

if __name__ == '__main__':
    import imctools.io.mcdparser as mcdp
    fn_mcd = '/home/vitoz/temp/txtvsmcd/20170805_p60-63_slide6_ac1_vz.mcd' 
    mcd = mcdp.McdParser(fn_mcd)
    ifw = ImcFolderWriter('/home/vitoz/temp/', mcddata=mcd)
    ifw.write_imc_folder()

    
