from imctools.io import mcdparser
from imctools.io import txtparser
import argparse
import os


def save_imc_to_tiff(imc_acquisition, acquisition='all', tifftype='ome', compression=0, outname=None, outpath=0,verbose=False):
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

    if verbose:
        print('Load filename %s' %imc_acquisition)

    if outname is None:
        outname = os.path.split(imc_acquisition)[1]
        outname = outname.rstrip('.mcd').rstrip('.txt')
        
    if outpath is None:
        outpath = os.path.split(imc_acquisition)[0]

    if imc_acquisition.endswith('.mcd'):
        acquisition_generator = _get_mcd_acquisition(imc_acquisition, acquisition=acquisition, verbose=verbose)
    elif imc_acquisition.endswith('.txt'):
        acquisition_generator = _get_txt_acquisition(imc_acquisition, acquisition_name='0', verbose=verbose)
    else:
        raise NameError('%s is not of type .mcd or .txt.' %imc_acquisition)

    for aid, imc_img in acquisition_generator:
        cur_outname = outname+'_a'+aid

        if tifftype == 'ome':
            cur_outname += '.ome.tiff'
        else:
            cur_outname += '.tiff'

        cur_outname = os.path.join(outpath, cur_outname)

        if verbose:
            print('Save %s as %s' %(aid,cur_outname))
        iw = imc_img.get_image_writer(cur_outname)
        iw.save_image(mode=tifftype, compression=compression)

        if verbose:
            print('Finished!')


def _get_mcd_acquisition(mcd_acquisition, acquisition='all', verbose=False):
    """
    A generator the returns the acquisitions
    :param mcd_acquisition:
    :param acquisition:
    :param verbose:
    :return:
    """
    with mcdparser.McdParser(mcd_acquisition) as mcd:
        n_ac = mcd.n_acquisitions
        if verbose:
            print('containing %i acquisitions:' % n_ac)

        ac_ids = mcd.acquisition_ids
        if verbose:
            for aid in ac_ids:
                print('%s \n' % aid)
            print('Print acquisition: %s' % acquisition)

        if args.acquisition == 'all':
            acquisitions = ac_ids
        else:
            acquisitions = [acquisition]

        for aid in acquisitions:
            imc_img = mcd.get_imc_acquisition(aid)
            acquisition = aid
            yield (acquisition, imc_img)


def _get_txt_acquisition(txt_acquisition, acquisition_name=None, verbose=False):
    """
    A generator the returns the acquisitions
    :param mcd_acquisition:
    :param acquisition:
    :param verbose:
    :return:
    """
    if acquisition_name is None:
        acquisition_name='0'
    txt = txtparser.TxtParser(txt_acquisition)
    if verbose:
        print('containing 1 acquisition')
    imc_img = txt.get_imc_acquisition()
    acquisition = acquisition_name
    yield (acquisition, imc_img)



if __name__ == "__main__":

    # Setup the command line arguments
    parser = argparse.ArgumentParser(description='Convert an IMC mcd or txt image to ImageJ Tiffs', prog='imc2tiff',
                                     usage='%(prog)s imc_filename [options]')
    parser.add_argument('imc_filename', metavar='mcd_filename', type=str,
                        help='The path to the mcd or txt IMC file to be converted')
    parser.add_argument('--acquisition', metavar='acquisition', type=str, default='all',
                        help='all or acquisition ID: acquisitions to write as tiff.')

    parser.add_argument('--tifftype',  type=str, default='ome',
                        help='ome or imagej: Write the files either with ome metadata or imagej compatible mode.'
                        )
    parser.add_argument('--compression', type=int, default=0,
                        help='0-9: Tiff compression level')

    parser.add_argument('--outname', type=str, default=None,
                        help='the name of the output file.')
    parser.add_argument('--outpath',type=str, default=None,
                        help='the output path.')

    # parse the arguments
    args = parser.parse_args()

    save_imc_to_tiff(imc_acquisition=args.imc_filename, acquisition=args.acquisition, tifftype=args.tifftype,
              compression=args.compression, outname=args.outname, outpath=args.outpath, verbose=True)


