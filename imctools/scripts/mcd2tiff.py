from imctools.io import mcdparser
import argparse


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
    parser.add_argument('--compression', metavar='compression', type=int, default=0,
                        help='0-9: Tiff compression level')


    # parse the arguments
    args = parser.parse_args()
    print('Load filename %s' %args.mcd_filename)

    fn = args.mcd_filename
    with mcdparser.McdParser(args.mcd_filename) as mcd:
        n_ac = mcd.n_acquisitions
        print('containing %i acquisitions:' % n_ac)
        ac_ids = mcd.acquisition_ids
        for aid in ac_ids:
            print('%s \n' %aid)

        print('Print acquisition: %s' %args.acquisition)

        if args.acquisition == 'all':
            acquisitions = ac_ids
        else:
            acquisitions = [args.acquisition]

        for aid in acquisitions:
            print('Save %s' %aid)
            imc_img = mcd.get_imc_acquisition(aid)
            outname = fn
            outname = outname.replace('.mcd', '_'+aid+'.tiff')
            iw = imc_img.get_image_writer(outname)
            iw.save_image(mode=args.tifftype, compression=args.compression)

        print('Finished!')

    # run the analysis
