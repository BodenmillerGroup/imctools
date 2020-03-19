import argparse
import os
import warnings

import pandas as pd
import numpy as np

from imctools.io import ometiffparser


def ometiff_2_analysis(
    filename,
    outfolder,
    basename,
    pannelcsv=None,
    metalcolumn=None,
    masscolumn=None,
    usedcolumn=None,
    addsum=False,
    bigtiff=True,
    sort_channels=True,
    pixeltype=None,
):
    warnings.warn(
        "imctools 1.x is deprecated, please migrate to version 2.x", DeprecationWarning
    )
    # read the pannelcsv to find out which channels should be loaded
    selmetals = None
    selmass = None

    outname = os.path.join(outfolder, basename)
    if pannelcsv is not None:

        pannel = pd.read_csv(pannelcsv)
        if pannel.shape[1] > 1:
            selected = pannel[usedcolumn]
            if masscolumn is None:
                metalcolumn = metalcolumn
                selmetals = [str(n) for s, n in zip(selected, pannel[metalcolumn]) if s]
            else:
                selmass = [str(n) for s, n in zip(selected, pannel[masscolumn]) if s]
        else:
            selmetals = [pannel.columns[0]] + pannel.iloc[:, 0].tolist()
    ome = ometiffparser.OmetiffParser(filename)
    imc_img = ome.get_imc_acquisition()

    if sort_channels:
        if selmetals is not None:

            def mass_from_met(x):
                return ("".join([m for m in x if m.isdigit()]), x)

            selmetals = sorted(selmetals, key=mass_from_met)
        if selmass is not None:
            selmass = sorted(selmass)

    writer = imc_img.get_image_writer(outname + ".tiff", metals=selmetals, mass=selmass)

    if addsum:
        img_sum = np.sum(writer.img_stack, axis=2)
        img_sum = np.reshape(img_sum, list(img_sum.shape) + [1])
        writer.img_stack = np.append(img_sum, writer.img_stack, axis=2)

    writer.save_image(mode="imagej", bigtiff=bigtiff, dtype=pixeltype)

    if selmass is not None:
        savenames = selmass

    elif selmetals is not None:
        savenames = selmetals
    else:
        savenames = [s for s in imc_img.channel_metals]

    if addsum:
        savenames = ["sum"] + savenames
    with open(outname + ".csv", "w") as f:
        for n in savenames:
            f.write(n + "\n")


if __name__ == "__main__":

    # Setup the command line arguments
    parser = argparse.ArgumentParser(
        description="Convert OME tiffs to analysis tiffs that are more compatible with tools.\n"
        + "A csv with a boolean column can be used to select subsets of channels or metals from the stack\n"
        + "The channels of the tiff will have the same order as in the csv.",
        prog="mcd2tiff",
        usage="%(prog)s ome_filename [options]",
    )

    parser.add_argument(
        "ome_filename", type=str, help="The path to the ome.tiff file to be converted"
    )

    parser.add_argument(
        "--outpostfix", type=str, default=None, help="the string to append to the name."
    )

    parser.add_argument(
        "--outfolder",
        type=str,
        default=None,
        help="the output folder, Default is a subfolder called analysis in the current folder.",
    )

    parser.add_argument(
        "--pannelcsv",
        type=str,
        default=None,
        help="name of the csv that contains the channels to be written out.",
    )

    parser.add_argument(
        "--metalcolumn",
        type=str,
        default="metal",
        help="Column name of the metal names.",
    )

    parser.add_argument(
        "--masscolumn",
        type=str,
        default=None,
        help="Column name of the mass names. If provided the metal column will be ignored.",
    )

    parser.add_argument(
        "--usedcolumn",
        type=str,
        default="ilastik",
        help="Column that should contain booleans (0, 1) if the channel should be used.",
    )
    parser.add_argument(
        "--outformat",
        type=str,
        default=None,
        choices=["float", "uint16", "uint8", "uint32"],
        help="""original or float, uint32, uint16, unit8\n
                                Per default the original pixeltype is taken""",
    )

    parser.add_argument(
        "--scale",
        type=str,
        default="no",
        choices=["no", "max", "percentile99, percentile99.9, percentile99.99"],
        help="scale the data?",
    )

    parser.add_argument(
        "--addsum",
        type=str,
        default="no",
        choices=["no", "yes"],
        help="Add the sum of the data as the first layer.",
    )

    parser.add_argument(
        "--bigtiff",
        type=str,
        default="yes",
        choices=["no", "yes"],
        help="Add the sum of the data as the first layer.",
    )
    parser.add_argument(
        "--sort_channels",
        type=str,
        default="yes",
        choices=["no", "yes"],
        help="Should the channels be sorted by mass?",
    )
    args = parser.parse_args()

    default_subfolder = "analysis"

    fn = args.ome_filename
    assert (fn[-9:] == ".ome.tiff") or (
        fn[-8:] == ".ome.tif"
    ) is True, "Must be an .ome.tiff or .ome.tif"

    fn_out = os.path.basename(fn).strip(".ome.tiff").strip(".ome.tif")

    outpostifx = args.outpostfix
    if outpostifx is not None:
        fn_out = "_".join([fn_out, outpostifx])

    outfolder = args.outfolder
    if outfolder is None:
        outfolder = os.path.join(os.path.split(fn)[0], default_subfolder)

    # create path if it doesnt exist
    if not (os.path.exists(outfolder)):
        os.mkdir(outfolder)

    # finalize the outname
    outname = os.path.join(outfolder, fn_out)

    ometiff_2_analysis(
        args.ome_filename,
        outfolder,
        fn_out,
        args.pannelcsv,
        args.metalcolumn,
        args.masscolumn,
        args.usedcolumn,
        args.addsum == "yes",
        bigtiff=args.bigtiff == "yes",
        sort_channels=args.sort_channels == "yes",
        pixeltype=args.outformat,
    )
