"""CLI interface for imctools library"""

import argparse

from imctools.converters.mcdfolder2imcfolder import mcd_folder_to_imc_folder


def main():
    """Main CLI entry point."""

    parser = argparse.ArgumentParser(prog="imctools", description="Tools to handle IMC data.")
    subparsers = parser.add_subparsers(help="sub-command help")

    mcd2imc_parser = subparsers.add_parser("mcdfolder2imcfolder", help="Converts a single MCD file to IMC-compatible folder.")
    mcd2imc_parser.add_argument("input_filename", type=str, help="Path to MCD input file")
    mcd2imc_parser.add_argument("output_folder", type=str, help="Output folder")
    mcd2imc_parser.set_defaults(func=mcd_folder_to_imc_folder)

    parser.parse_args()


def _mcd_folder_to_imc_folder(args):
    mcd_folder_to_imc_folder(args.input_filename, args.output_folder)
