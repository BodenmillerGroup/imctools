"""CLI interface for imctools library"""

import argparse

from imctools.converters.mcdfolder2imcfolder import mcdfolder_to_imcfolder


def main():
    """Main CLI entry point."""

    parser = argparse.ArgumentParser(prog="imctools", description="Tools to handle IMC data.")
    subparsers = parser.add_subparsers(help="sub-command help")

    mcd2imc_parser = subparsers.add_parser("mcdfolder2imcfolder", help="Converts a folder or zip file of raw data (.mcd + .txt) to IMC folder.")
    mcd2imc_parser.add_argument("input", help="The path to the folder/zip archive containing the IMC raw data")
    mcd2imc_parser.add_argument("output_folder", help="Path to the output folder")
    mcd2imc_parser.add_argument("--zip", action="store_true", help="Whether to create an output as .zip file")
    mcd2imc_parser.add_argument("--skip-csv", action="store_true", help="Whether to skip creation of CSV metadata files")
    mcd2imc_parser.set_defaults(func=_mcdfolder_to_imcfolder)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


def _mcdfolder_to_imcfolder(args):
    mcdfolder_to_imcfolder(args.input, args.output_folder, args.zip, args.skip_csv)
