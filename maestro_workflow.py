#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os

from scripts.file_separate import separate_ligands
from scripts.SMARTS_extract import unzip, SMARTS_extract


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--docking", help="Input file from docking. Unzipped. *_pv.maegz")
    parser.add_argument("-c", "--crystal", help="Input file with crystals.")
    parser.add_argument("-o", "--output", help="Output filename.", default="maestro_script.txt")
    parser.add_argument("-r", "--remove", help="Clear created temp files and folders after finished run. Default: True", action="store_false")

    args = parser.parse_args()

    def cleanup():
        """
        Cleans files and folders after finished run.
        """

        paths = ["./ligands", "./docking", "./workspace"]  # Folders to clean.
        for path in paths:
            for file in os.listdir(path):
                os.remove('/'.join([path, file]))
            os.rmdir(path)


    def main():
        """
        Main function. Creates Maestro script.
        """

        try:
            os.mkdir("./workspace")  # Folder for temporary files
        except FileExistsError:
            print("Workspace already exists, cleaning old files...")  # ... to avoid possible FileExistsError conflicts.
            for i in os.listdir("./workspace"):
                os.remove("./workspace/%s" % i)

        unzipped = unzip(args.docking, "workspace")  # SMARTS_extract.py

        SMARTS = SMARTS_extract(unzipped, "docking", "workspace")  # SMARTS_extract.py

        os.system("sudo /opt/schrodingerfree/run pv_convert.py -mode merge %s" % unzipped)

        input_file = ""
        for i in os.listdir("./workspace"):
            if unzipped.rstrip("_pv.mae") in i and "out_complex" in i and "maegz" not in i:
                input_file = i
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

        output = open(args.output, "w")
        output.write('entryimport "%s"\nentryimport "%s"\nshowpanel superimpose\n\n' % (args.crystal, os.path.abspath('/'.join(["./workspace" + input_file]))))

        for i in range(len(titles_file)):
            output.write("entrywsincludeonly s_m_title *%s*\n" % '_'.join(titles_file[i].split('_')[:2]))
            output.write("entrywsinclude s_m_title %s\n" % '_'.join(titles_file[i].split('_')[:1]))
            output.write('propertysuperimposesetting  applytoentries=included\nsuperimpose  inplace=false\nsuperimposeset atom.ptype " CA "\nsuperimpose  inplace=true\n')
            output.write('superimposesmarts "%s" \n\n' % SMARTS[i].rstrip())

        output.close()

        if args.remove:
            cleanup()

    main()


# TODO os.path.abspath dla normalizacji ścieżek?
# TODO requirements.txt, README.md
