"""CLI interface for imctools library"""

import argparse

from imctools.converters import (
    mcdfolder_to_imcfolder,
    omefolder_to_histocatfolder,
    omefile_to_histocatfolder,
    omefile_to_tifffolder,
    omefile_2_analysisfolder,
    export_acquisition_csv,
    probability_to_uncertainty,
)
from imctools.converters.exportacquisitioncsv import AC_META


def main():
    """Main CLI entry point."""

    parser = argparse.ArgumentParser(prog="imctools", description="Tools to handle Fluidigm IMC data.")
    subparsers = parser.add_subparsers(help="Sub-command help.")

    _add_mcdfolder2imcfolder_parser(subparsers)
    _add_omefolder2histocatfolder_parser(subparsers)
    _add_omefile2histocatfolder_parser(subparsers)
    _add_omefile2tifffolder_parser(subparsers)
    _add_omefile2analysisfolder_parser(subparsers)
    _add_exportacquisitioncsv_parser(subparsers)

    # main entry point
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


def _add_mcdfolder2imcfolder_parser(subparsers: argparse._SubParsersAction):
    def func(args):
        mcdfolder_to_imcfolder(args.input, args.output_folder, args.zip, args.skip_csv)

    parser = subparsers.add_parser(
        "mcdfolder2imcfolder",
        description="Converts a folder or zip file of raw data (.mcd and .txt) to IMC folder.",
        help="Converts a folder or zip file of raw data (.mcd and .txt) to IMC folder.",
    )
    parser.add_argument("input", help="Path to the folder/zip archive containing the IMC raw data.")
    parser.add_argument("output_folder", help="Path to the output folder.")
    parser.add_argument("--zip", action="store_true", help="Whether to create an output as .zip file.")
    parser.add_argument("--skip-csv", action="store_true", help="Whether to skip creation of CSV metadata files.")
    parser.set_defaults(func=func)


def _add_omefolder2histocatfolder_parser(subparsers: argparse._SubParsersAction):
    def func(args):
        omefolder_to_histocatfolder(
            args.input_folder, args.output_folder, args.mask_folder, args.mask_suffix, args.imagetype
        )

    parser = subparsers.add_parser(
        "omefolder2histocatfolder",
        description="Converts all OME-TIFF files in input folder to a folder compatible with HistoCAT software.",
        help="Converts all OME-TIFF files in input folder to a folder compatible with HistoCAT software.",
    )
    parser.add_argument("input_folder", help="Input folder with OME-TIFF files.")
    parser.add_argument("output_folder", help="Output folder.")
    parser.add_argument("--mask_folder", help="Folder containing the masks, or single mask file.", default=None)
    parser.add_argument("--mask_suffix", help="Suffix of the mask TIFFs.", default="_mask.tiff")
    parser.add_argument(
        "--imagetype", help="The output image type.", default=None, choices=[None, "uint16", "int16", "float"]
    )
    parser.set_defaults(func=func)


def _add_omefile2histocatfolder_parser(subparsers: argparse._SubParsersAction):
    def func(args):
        omefile_to_histocatfolder(args.filename, args.base_folder, args.mask_file, args.imagetype)

    parser = subparsers.add_parser(
        "omefile2histocatfolder",
        description="Converts single OME-TIFF file to a folder compatible with HistoCAT software.",
        help="Converts single OME-TIFF file to a folder compatible with HistoCAT software.",
    )
    parser.add_argument("filename", help="Path to OME-TIFF input file.")
    parser.add_argument("base_folder", help="Base output folder.")
    parser.add_argument("--mask_file", help="Path to mask file.", default=None)
    parser.add_argument(
        "--imagetype", help="The output image type.", default=None, choices=[None, "uint16", "int16", "float"]
    )
    parser.set_defaults(func=func)


def _add_omefile2tifffolder_parser(subparsers: argparse._SubParsersAction):
    def func(args):
        omefile_to_tifffolder(args.filename, args.output_folder, args.basename, args.imagetype)

    parser = subparsers.add_parser(
        "omefile2tifffolder",
        description="Saves planes of single OME-TIFF file to a folder containing standard TIFF (ImageJ-compatible) files.",
        help="Saves planes of single OME-TIFF file to a folder containing standard TIFF (ImageJ-compatible) files.",
    )
    parser.add_argument("filename", help="Path to OME-TIFF input file.")
    parser.add_argument("output_folder", help="Output folder.")
    parser.add_argument("--basename", help="Basename for generated output files.", default=None)
    parser.add_argument(
        "--imagetype", help="The output image type.", default=None, choices=[None, "uint16", "int16", "float"]
    )
    parser.set_defaults(func=func)


def _add_omefile2analysisfolder_parser(subparsers: argparse._SubParsersAction):
    def func(args):
        omefile_2_analysisfolder(
            args.filename,
            args.output_folder,
            args.basename,
            args.pannelcsv,
            args.metalcolumn,
            args.masscolumn,
            args.usedcolumn,
            args.addsum,
            args.bigtiff,
            not args.nosort,  # Invert argument value!
            args.imagetype,
        )

    parser = subparsers.add_parser(
        "omefile2analysisfolder",
        description="Converts single OME-TIFF file to folder compatible with IMC segmentation pipeline.",
        help="Converts single OME-TIFF file to folder compatible with IMC segmentation pipeline.",
    )
    parser.add_argument("filename", help="Path to OME-TIFF input file.")
    parser.add_argument("output_folder", help="Output folder.")
    parser.add_argument("--basename", help="Basename for generated output files.", default=None)
    parser.add_argument(
        "--pannelcsv", help="Name of the CSV file that contains the channels to be written out.", default=None
    )
    parser.add_argument("--metalcolumn", help="Column name of the metal names.", default="Metal Tag")
    parser.add_argument(
        "--masscolumn",
        help="Column name of the mass names. If provided the metal column will be ignored.",
        default=None,
    )
    parser.add_argument(
        "--usedcolumn",
        help="Column that should contain booleans (0, 1) if the channel should be used.",
        default="ilastik",
    )
    parser.add_argument("--addsum", action="store_true", help="Add the sum of the data as the first layer.")
    parser.add_argument("--bigtiff", action="store_true", help="Whether to save TIFF files in BigTIFF format.")
    parser.add_argument("--nosort", action="store_true", help="Whether to skip sorting channels by mass.")
    parser.add_argument(
        "--imagetype", help="The output image type.", default=None, choices=[None, "uint16", "int16", "float"]
    )
    parser.set_defaults(func=func)


def _add_exportacquisitioncsv_parser(subparsers: argparse._SubParsersAction):
    def func(args):
        export_acquisition_csv(args.ome_folder, args.output_folder, args.output_name)

    parser = subparsers.add_parser(
        "exportacquisitioncsv",
        description="Reads all the acquisition metadata from the ome folders and concatenates them to a csv that contains all the metadata.",
        help="Reads all the acquisition metadata from the ome folders and concatenates them to a csv that contains all the metadata.",
    )
    parser.add_argument("ome_folder", help="The path to the folders containing the OME-TIFFs.")
    parser.add_argument("output_folder", help="Folder where the metadata CSV file should be stored in.")
    parser.add_argument("--output_name", help="Filename of the acquisition metadata CSV file.", default=AC_META)
    parser.set_defaults(func=func)


def _add_probability2uncertainty_parser(subparsers: argparse._SubParsersAction):
    def func(args):
        probability_to_uncertainty(args.ome_folder, args.output_folder, args.output_name)

    parser = subparsers.add_parser(
        "probability2uncertainty",
        description="Converts probability masks to uncertainties.",
        help="Converts probability masks to uncertainties.",
    )
    parser.add_argument("filename", help="The path to the probability TIFF file.")
    parser.add_argument(
        "--output_folder",
        help="Folder to save the images in. By default a sub-folder with the basename image_filename in the image_filename folder.",
        default=None,
    )
    parser.add_argument("--basename", help="Basename for the output image. Default: image_filename", default=None)
    parser.set_defaults(func=func)
