#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os

from scripts.file_separate import separate_ligands
from scripts.SMARTS_extract import unzip, SMARTS_extract
from scripts.utils import create_folder, maestro_writer, cleanup
from scripts.configuration_scripts import CONFIGURE

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--docking", help="input file from docking, zipped *_pv.maegz")
    parser.add_argument("-c", "--crystal", help="input file with crystals")
    parser.add_argument("-o", "--output", help="output filename", default="maestro_script.cmd")
    parser.add_argument("-r", "--remove", help="clear created temp files and folders after finished run; default: False", action="store_true")
    parser.add_argument("-u", "--update", help="update gloabal variables; default: False", action="store_true")

    args = parser.parse_args()

    def main():
        """
        Main function. Creates Maestro script.
        """

        # Storing paths to files and normalizing them
        GLOBAL_VARIABLES = CONFIGURE(args.update)  # utils.py
        GLOBAL_VARIABLES[0]=GLOBAL_VARIABLES[0].strip()
        GLOBAL_VARIABLES[1]=GLOBAL_VARIABLES[1].strip()

        workspace_folder = os.path.abspath("./workspace")
        docking_folder = os.path.abspath("./docking")
        docking_file = os.path.abspath(args.docking)
        ligands_folder = os.path.abspath("./ligands")

        create_folder(workspace_folder, True)  # utils.py

        unzipped, unzipped_name = unzip(GLOBAL_VARIABLES[1],docking_file, GLOBAL_VARIABLES[0], workspace_folder)  # SMARTS_extract.py

        SMARTS = SMARTS_extract(GLOBAL_VARIABLES[1], unzipped, GLOBAL_VARIABLES[0], workspace_folder)  # SMARTS_extract.py

        print(workspace_folder+"/"+unzipped_name)
        os.system("%s %s/run pv_convert.py -mode merge %s.mae" % (GLOBAL_VARIABLES[1], GLOBAL_VARIABLES[0], workspace_folder+"/"+unzipped_name))

        print(unzipped_name[:-3]+"-out_complex.mae")
        input_file = ""
        for i in os.listdir(workspace_folder):
            #if unzipped.rstrip("_pv.mae") in i and "out_complex" in i and "maegz" not in i:
            if i==unzipped_name[:-3]+"-out_complex.mae":
                input_file = "/".join([workspace_folder, i])
                break

        titles_file = []
        if input_file:
            error_code, titles_file = separate_ligands(input_file, ligands_folder)  # file_separate.py
            if error_code != 0:
                parser.print_help()
                exit(error_code)
        else:
            print("File not found - complex.")
            exit()

        maestro_writer(args.output, args.crystal, input_file, titles_file, SMARTS, 0)  # utils.py

        if args.remove:
            paths = [ligands_folder, docking_folder, workspace_folder]  # Folders to clean.
            cleanup(paths)  # utils.py

    main()

# TODO README.md
# TODO sudo
# TODO wyeksportować plik pv_convert -> out.complex
