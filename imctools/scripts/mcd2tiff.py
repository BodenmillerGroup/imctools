from imctools.io import mcdparser
import argparse
import os

def save_tiff(mcd_filename, acquisition='all', tifftype='ome', compression=0, outname=None, outpath=0,verbose=False):
    """

    :param mcd_filename:
    :param acquisition:
    :param tifftype:
    :param compression:
    :param outname:
    :param outpath:
    :return:
    """

    # parse the arguments
    args = parser.parse_args()
    if verbose:
        print('Load filename %s' %mcd_filename)

    if outname is None:
        outname = os.path.split(mcd_filename)[1]
        outname = outname.replace('.mcd', '')

    if outpath is None:
        outpath = os.path.split(mcd_filename)[0]

    with mcdparser.McdParser(mcd_filename) as mcd:
        n_ac = mcd.n_acquisitions
        if verbose:
            print('containing %i acquisitions:' % n_ac)

        ac_ids = mcd.acquisition_ids
        if verbose:
            for aid in ac_ids:
                print('%s \n' %aid)
            print('Print acquisition: %s' %acquisition)

        if args.acquisition == 'all':
            acquisitions = ac_ids
        else:
            acquisitions = [acquisition]

        for aid in acquisitions:
            imc_img = mcd.get_imc_acquisition(aid)
            cur_outname = outname + '_a' + aid

            if tifftype == 'ome':
                cur_outname += '.ome.tiff'
            else:
                cur_outname +='.tiff'

            cur_outname = os.path.join(outpath, cur_outname)

            if verbose:
                print('Save %s as %s' %(aid,cur_outname))
            iw = imc_img.get_image_writer(cur_outname)
            iw.save_image(mode=tifftype, compression=compression)

        if verbose:
            print('Finished!')


if __name__ == "__main__":

    # Setup the command line arguments
    parser = argparse.ArgumentParser(description='Convert MCD to ImageJ Tiffs', prog='mcd2tiff', usage='%(prog)s mcd_filename [options]')
    parser.add_argument('mcd_filename', metavar='mcd_filename', type=str,
                        help='The path to the MCD file to be converted')
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

    save_tiff(mcd_filename=args.mcd_filename, acquisition=args.acquisition, tifftype=args.tifftype,
              compression=args.compression, outname=args.outname, outpath=args.outpath, verbose=True)


