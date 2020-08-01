#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os

from scripts.file_separate import separate_ligands
from scripts.SMARTS_extract import unzip, SMARTS_extract
from scripts.utils import create_folder, maestro_writer, cleanup, CONFIGURE


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--docking", help="input file from docking, unzipped *_pv.maegz")
    parser.add_argument("-c", "--crystal", help="input file with crystals")
    parser.add_argument("-o", "--output", help="output filename", default="maestro_script.txt")
    parser.add_argument("-r", "--remove", help="clear created temp files and folders after finished run; default: False", action="store_true")
    parser.add_argument("-u", "--update", help="update gloabal variables; default: False", action="store_true")

    args = parser.parse_args()

    def main():
        """
        Main function. Creates Maestro script.
        """

        GLOBAL_VARIABLES = CONFIGURE(args.update)  # utils.py

        create_folder("./workspace", True)  # utils.py

        unzipped = unzip(args.docking, "workspace")  # SMARTS_extract.py

        SMARTS = SMARTS_extract(unzipped, "docking", "workspace")  # SMARTS_extract.py

        # os.system("sudo /opt/schrodingerfree/run pv_convert.py -mode merge %s" % unzipped)
        os.system("sudo %s/run pv_convert.py -mode merge %s" % (GLOBAL_VARIABLES[0], unzipped))

        input_file = ""
        for i in os.listdir("./workspace"):
            if unzipped.rstrip("_pv.mae") in i and "out_complex" in i and "maegz" not in i:
                input_file = "/".join(["./workspace", i])
                break

        titles_file = []
        if input_file:
            error_code, titles_file = separate_ligands(input_file, "ligands")  # file_separate.py
            if error_code != 0:
                parser.print_help()
                exit(error_code)
        else:
            print("File not found - complex.")
            exit()

        maestro_writer(args.output, args.crystal, input_file, titles_file, SMARTS)  # utils.py

        if args.remove:
            paths = ["./ligands", "./docking", "./workspace"]  # Folders to clean.
            cleanup(paths)  # utils.py

    main()


# TODO os.path.abspath dla normalizacji ścieżek?
# TODO requirements.txt, README.md
# TODO sudo
# TODO wyeksportować plik pv_convert -> out.complex
