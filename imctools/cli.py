"""CLI interface for imctools library"""

import argparse

from imctools.converters import (
    mcdfolder_to_imcfolder,
    omefolder_to_histocatfolder,
    omefile_to_histocatfolder,
    omefile_to_tifffolder,
    omefile_2_analysisfolder,
)


def main():
    """Main CLI entry point."""

    parser = argparse.ArgumentParser(prog="imctools", description="Tools to handle Fluidigm IMC data.")
    subparsers = parser.add_subparsers(help="sub-command help")

    # mcdfolder2imcfolder parser
    mcdfolder2imcfolder_parser = subparsers.add_parser(
        "mcdfolder2imcfolder",
        description="Converts a folder or zip file of raw data (.mcd and .txt) to IMC folder.",
        help="Converts a folder or zip file of raw data (.mcd and .txt) to IMC folder.",
    )
    mcdfolder2imcfolder_parser.add_argument("input", help="path to the folder/zip archive containing the IMC raw data")
    mcdfolder2imcfolder_parser.add_argument("output_folder", help="path to the output folder")
    mcdfolder2imcfolder_parser.add_argument(
        "--zip", action="store_true", help="whether to create an output as .zip file"
    )
    mcdfolder2imcfolder_parser.add_argument(
        "--skip-csv", action="store_true", help="whether to skip creation of CSV metadata files"
    )
    mcdfolder2imcfolder_parser.set_defaults(func=_mcdfolder_to_imcfolder)

    # omefolder2histocatfolder parser
    omefolder2histocatfolder_parser = subparsers.add_parser(
        "omefolder2histocatfolder",
        description="Converts all OME-TIFF files in input folder to a folder compatible with HistoCAT software.",
        help="Converts all OME-TIFF files in input folder to a folder compatible with HistoCAT software.",
    )
    omefolder2histocatfolder_parser.add_argument("input_folder", help="input folder with OME-TIFF files")
    omefolder2histocatfolder_parser.add_argument("output_folder", help="output folder")
    omefolder2histocatfolder_parser.add_argument(
        "--mask_folder", help="folder containing the masks, or single mask file", default=None
    )
    omefolder2histocatfolder_parser.add_argument("--mask_suffix", help="suffix of the mask TIFFs", default="_mask.tiff")
    omefolder2histocatfolder_parser.add_argument(
        "--imagetype", help="The output image type", default=None, choices=[None, "uint16", "int16", "float"]
    )
    omefolder2histocatfolder_parser.set_defaults(func=_omefolder_to_histocatfolder)

    # omefile2histocatfolder parser
    omefile2histocatfolder_parser = subparsers.add_parser(
        "omefile2histocatfolder",
        description="Converts single OME-TIFF file to a folder compatible with HistoCAT software.",
        help="Converts single OME-TIFF file to a folder compatible with HistoCAT software.",
    )
    omefile2histocatfolder_parser.add_argument("filename", help="path to OME-TIFF input file")
    omefile2histocatfolder_parser.add_argument("base_folder", help="base output folder")
    omefile2histocatfolder_parser.add_argument("--mask_file", help="path to mask file", default=None)
    omefile2histocatfolder_parser.add_argument(
        "--imagetype", help="The output image type", default=None, choices=[None, "uint16", "int16", "float"]
    )
    omefile2histocatfolder_parser.set_defaults(func=_omefile_to_histocatfolder)

    # omefile2tifffolder parser
    omefile2tifffolder_parser = subparsers.add_parser(
        "omefile2tifffolder",
        description="Saves planes of single OME-TIFF file to a folder containing standard TIFF (ImageJ-compatible) files.",
        help="Saves planes of single OME-TIFF file to a folder containing standard TIFF (ImageJ-compatible) files.",
    )
    omefile2tifffolder_parser.add_argument("filename", help="path to OME-TIFF input file")
    omefile2tifffolder_parser.add_argument("output_folder", help="output folder")
    omefile2tifffolder_parser.add_argument("--basename", help="basename for generated output files", default=None)
    omefile2tifffolder_parser.add_argument(
        "--imagetype", help="The output image type", default=None, choices=[None, "uint16", "int16", "float"]
    )
    omefile2tifffolder_parser.set_defaults(func=_omefile_to_tifffolder)

    # main entry point
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


def _mcdfolder_to_imcfolder(args):
    mcdfolder_to_imcfolder(args.input, args.output_folder, args.zip, args.skip_csv)


def _omefolder_to_histocatfolder(args):
    omefolder_to_histocatfolder(
        args.input_folder, args.output_folder, args.mask_folder, args.mask_suffix, args.imagetype
    )


def _omefile_to_histocatfolder(args):
    omefile_to_histocatfolder(args.filename, args.base_folder, args.mask_file, args.imagetype)


def _omefile_to_tifffolder(args):
    omefile_to_tifffolder(args.filename, args.output_folder, args.basename, args.imagetype)


def _omefile_2_analysisfolder(args):
    omefile_2_analysisfolder(
        args.filename,
        args.output_folder,
        args.basename,
        args.panel_csv_file,
        args.metalcolumn,
        args.masscolumn,
        args.usedcolumn,
        args.add_sum,
        args.bigtiff,
        args.sort_channels,
        args.imagetype,
    )
