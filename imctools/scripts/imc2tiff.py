#! /usr/bin/env python
import warnings

from imctools.io import mcdparser
from imctools.io import txtparser
import argparse
import os
import glob
from imctools.external import temporarydirectory
import zipfile

TXT_FILENDING = ".txt"
MCD_FILENDING = ".mcd"
TIFF_FILENDING = ".tiff"
OME_FILENDING = ".ome.tiff"
ZIP_FILENDING = ".zip"

IMC_FILENDINGS = (TXT_FILENDING, MCD_FILENDING)


def save_imc_to_tiff(
    imc_acquisition,
    acquisition="all",
    tifftype="ome",
    compression=0,
    outname=None,
    outpath=None,
    zip_filetype=None,
    verbose=False,
):
    """
    :param imc_acquisition:
    :param acquisition:
    :param tifftype:
    :param compression:
    :param outname:
    :param outpath:
    :param verbose:
    :return:
    """
    warnings.warn(
        "imctools 1.x is deprecated, please migrate to version 2.x", DeprecationWarning
    )

    if verbose:
        print("Load filename %s" % imc_acquisition)

    if outpath is None:
        outpath = os.path.split(imc_acquisition)[0]

    if zip_filetype is None:
        zip_filetype = ""

    if imc_acquisition.endswith(IMC_FILENDINGS):
        if outname is None:
            outname = os.path.split(imc_acquisition)[1]
        for end in IMC_FILENDINGS:
            outname = outname.rstrip(end)
        if imc_acquisition.endswith(MCD_FILENDING):
            acquisition_generator = _get_mcd_acquisition(
                imc_acquisition, acquisition=acquisition, verbose=verbose
            )
        elif imc_acquisition.endswith(TXT_FILENDING):
            acquisition_generator = _get_txt_acquisition(
                imc_acquisition, acquisition_name="0", verbose=verbose
            )

        for aid, imc_img in acquisition_generator:
            cur_outname = outname + "_a" + aid

            if tifftype == "ome":
                cur_outname += OME_FILENDING
            else:
                cur_outname += TIFF_FILENDING

            cur_outname = os.path.join(outpath, cur_outname)

            if verbose:
                print("Save %s as %s" % (aid, cur_outname))
            iw = imc_img.get_image_writer(cur_outname)
            iw.save_image(mode=tifftype, compression=compression)

    elif imc_acquisition.endswith(ZIP_FILENDING):
        convert_imczip2tiff(
            imc_acquisition,
            outpath,
            common_filepart=zip_filetype,
            acquisition=acquisition,
            tifftype=tifftype,
            compression=compression,
            outname=outname,
            verbose=False,
        )
    else:
        raise NameError("%s is not of type .mcd, .txt or .zip" % imc_acquisition)

    if verbose:
        print("Finished!")


def convert_imcfolders2tiff(folders, output_folder, common_filepart=None, **kwargs):
    """
    Converts a list of folders into ome.tiffs
    :param folder:
    :param output_folder:
    :param common_filepart:
    :return:
    """

    failed_images = list()
    if common_filepart is None:
        common_filepart = ""

    for fol in folders:
        for fn in glob.glob(os.path.join(fol, "*")):
            if (common_filepart in os.path.basename(fn)) & (
                fn.endswith(IMC_FILENDINGS) | fn.endswith(ZIP_FILENDING)
            ):
                txtname = fn
                try:
                    save_imc_to_tiff(txtname, outpath=output_folder, **kwargs)
                except:
                    failed_images.append(txtname)

    if len(failed_images) > 0:
        print("Failed images:\n")
        print(failed_images)


def convert_imczip2tiff(zipfn, output_folder, common_filepart=None, **kwargs):
    """
    Converts a zip archive containing IMC files to tiff

    """
    if common_filepart is None:
        common_filepart = ""
    with temporarydirectory.TemporaryDirectory() as tempdir:
        with zipfile.ZipFile(zipfn, allowZip64=True) as zipf:
            for fn in zipf.namelist():
                if (common_filepart in fn) & fn.endswith(IMC_FILENDINGS):
                    zipf.extract(fn, tempdir)
        convert_imcfolders2tiff(
            [tempdir], output_folder, common_filepart=common_filepart, **kwargs
        )


def _get_mcd_acquisition(
    mcd_acquisition, acquisition="all", verbose=False, filehandle=None
):
    """
    A generator the returns the acquisitions
    :param mcd_acquisition:
    :abstractparseram acquisition:
    :param verbose:
    :return:
    """
    with mcdparser.McdParser(mcd_acquisition, filehandle) as mcd:
        n_ac = mcd.n_acquisitions
        if verbose:
            print("containing %i acquisitions:" % n_ac)

        ac_ids = mcd.acquisition_ids
        if verbose:
            for aid in ac_ids:
                print("%s \n" % aid)
            print("Print acquisition: %s" % acquisition)

        if acquisition == "all":
            acquisitions = ac_ids
        else:
            acquisitions = [acquisition]

        for aid in acquisitions:
            imc_img = mcd.get_imc_acquisition(aid)
            acquisition = aid
            yield (acquisition, imc_img)


def _get_txt_acquisition(
    txt_acquisition, acquisition_name=None, verbose=False, filehandle=None
):
    """
    A generator the returns the acquisitions
    :param mcd_acquisition:
    :param acquisition:
    :param verbose:
    :return:
    """
    if acquisition_name is None:
        acquisition_name = "0"
    txt = txtparser.TxtParser(txt_acquisition, filehandle)
    if verbose:
        print("containing 1 acquisition")
    imc_img = txt.get_imc_acquisition()
    acquisition = acquisition_name
    yield (acquisition, imc_img)


if __name__ == "__main__":

    # Setup the command line arguments
    parser = argparse.ArgumentParser(
        description="Convert an IMC mcd or txt image to ImageJ Tiffs",
        prog="imc2tiff",
        usage="%(prog)s imc_filename [options]",
    )
    parser.add_argument(
        "imc_filename",
        metavar="mcd_filename",
        type=str,
        help="The path to the mcd or txt IMC file to be converted",
    )
    parser.add_argument(
        "--acquisition",
        metavar="acquisition",
        type=str,
        default="all",
        help="all or acquisition ID: acquisitions to write as tiff.",
    )

    parser.add_argument(
        "--tifftype",
        type=str,
        default="ome",
        help="ome or imagej: Write the files either with ome metadata or imagej compatible mode.",
    )
    parser.add_argument(
        "--compression", type=int, default=0, help="0-9: Tiff compression level"
    )

    parser.add_argument(
        "--outname", type=str, default=None, help="the name of the output file."
    )
    parser.add_argument("--outpath", type=str, default=None, help="the output path.")

    # parse the arguments
    args = parser.parse_args()
    imc_filename = args.imc_filename

    save_imc_to_tiff(
        imc_acquisition=args.imc_filename,
        acquisition=args.acquisition,
        tifftype=args.tifftype,
        compression=args.compression,
        outname=args.outname,
        outpath=args.outpath,
        verbose=True,
    )
