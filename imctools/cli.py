"""CLI interface for imctools library"""

import argparse

from imctools.io.mcd.mcdparser import convert_mcd_to_imc_folder
from imctools.io.txt.txtparser import convert_txt_to_imc_folder


def main():
    """Main CLI entry point."""

    parser = argparse.ArgumentParser(prog="imctools", description="Tools to handle IMC data.")
    subparsers = parser.add_subparsers(help="sub-command help")

    mcd2imc_parser = subparsers.add_parser("mcd2imc", help="Converts a single MCD file to IMC-compatible folder.")
    mcd2imc_parser.add_argument("input_filename", type=str, help="Path to MCD input file")
    mcd2imc_parser.add_argument("output_folder", type=str, help="Output folder")
    mcd2imc_parser.set_defaults(func=_mcd2imc)

    txt2imc_parser = subparsers.add_parser("txt2imc", help="Converts a single TXT file to IMC-compatible folder.")
    txt2imc_parser.add_argument("input_filename", type=str, help="Path to TXT input file")
    txt2imc_parser.add_argument("output_folder", type=str, help="Output folder")
    txt2imc_parser.set_defaults(func=_txt2imc)

    parser.parse_args()


def _mcd2imc(args):
    """Converts a single MCD file to IMC-compatible folder."""
    convert_mcd_to_imc_folder(args.input_filename, args.output_folder)


def _txt2imc(args):
    """Converts a single TXT file to IMC-compatible folder."""
    convert_txt_to_imc_folder(args.input_filename, args.output_folder)
