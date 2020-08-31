#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse

from scripts.file_separate import separate_ligands
from scripts.configuration_scripts import CONFIGURE


def unzip(zipped_file, tool_path, folder="."):
    """
    Unzip file from docking

    :param str tool_path: path to schroedinger
    :param str zipped_file: file from docking
    :param str folder: folder name to save unzipped version of the file

    :return str unzipped: returns path to unzipped file
    """

    base = os.path.basename(zipped_file)
    unzipped = "/".join([folder, os.path.splitext(base)[0] + ".mae"])

    os.system("sudo %s/run structconvert.py -imae %s %s" % (tool_path, zipped_file, unzipped))  # Convert zipped file after docking to unzipped version.
    return unzipped


def SMARTS_extract(sudo_var, unzipped, tool_path, folder=".", temp_file_loc="."):
    """
    From each file extract SMARTS to temporary file and store value in a list.

    :param str sudo_var: required sudo perm?
    :param str tool_path: path to schroedinger
    :param str unzipped: unzipped file from docking
    :param str folder: workspace folder, where separated files are saved
    :param str temp_file_loc: temporary DELETE file location

    :return list SMARTS_save: List of SMARTS in the same order as in input file (unzipped)
    """

    error_code, titles_SMARTS = separate_ligands(unzipped, folder)  # Separate entries - file_separate.py
    if error_code != 0:
        parser.print_help()
        exit(error_code)

    SMARTS_save = []

    for i in range(1, len(titles_SMARTS)):
        try:
            # os.system("sudo /opt/schrodingerfree/run gen_smarts.py %s/%s.mae %s/DELETE > void" % (folder, titles_SMARTS[i], temp_file_loc))
            os.system("%s %s/run gen_smarts.py %s/%s.mae %s/DELETE" % (sudo_var, tool_path, folder, titles_SMARTS[i], temp_file_loc))
            temp = open("%s/DELETE" % temp_file_loc)
            temp1 = temp.read()
            SMARTS_save.append(temp1)
            temp.close()
        except ValueError:
            print("ERROR: %s" % titles_SMARTS[i])
    os.remove("%s/DELETE" % temp_file_loc)
    return SMARTS_save


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to unzip and extract SMARTS from files after docking.")

    inp = parser.add_argument_group("input files type. Exactly one is required")
    inp.add_argument("-z", "--zipped", help="zipped file from docking")
    inp.add_argument("-u", "--unzipped", help="unzipped file from docking")

    parser.add_argument("-f", "--folder", help="workspace folder", default=".")
    parser.add_argument("--update", help="update gloabal variables; default: False", action="store_true")
    args = parser.parse_args()

    GLOBAL_VARIABLES = CONFIGURE(args.update)  # utils.py

    SMARTS = ""
    if args.zipped and args.unzipped:
        parser.print_help()
        exit()
    if args.zipped:
        unzipped_file = unzip(os.path.abspath(args.zipped), GLOBAL_VARIABLES[0])
        SMARTS = SMARTS_extract(required, os.path.abspath(unzipped_file), GLOBAL_VARIABLES[0])
    if args.unzipped:
        SMARTS = SMARTS_extract(required, os.path.abspath(args.unzipped), GLOBAL_VARIABLES[0])
    else:
        parser.print_help()
        exit()
    print(SMARTS)
