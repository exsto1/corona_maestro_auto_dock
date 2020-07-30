#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse

from scripts.file_separate import separate_ligands


def unzip(zipped_file, folder="."):
    """
    Unzip file from docking

    :param str zipped_file: file from docking
    :param str folder: folder name to save unzipped version of the file

    :return str unzipped: returns path to unzipped file
    """

    base = os.path.basename(zipped_file)
    unzipped = "/".join([folder, os.path.splitext(base)[0] + ".mae"])

    os.system("sudo /opt/schrodingerfree/run structconvert.py -imae %s %s" % (zipped_file, unzipped))  # Convert zipped file after docking to unzipped version.
    return unzipped


def SMARTS_extract(unzipped, folder=".", temp_file_loc="."):
    """
    From each file extract SMARTS to temporary file and store value in a list.

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
            os.system("sudo /opt/schrodingerfree/run gen_smarts.py %s/%s.mae %s/DELETE > void" % (folder, titles_SMARTS[i], temp_file_loc))
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
    args = parser.parse_args()

    SMARTS = ""
    if args.zipped and args.unzipped:
        parser.print_help()
        exit()
    if args.zipped:
        unzipped_file = unzip(args.zipped)
        SMARTS = SMARTS_extract(unzipped_file)
    if args.unzipped:
        SMARTS = SMARTS_extract(args.unzipped)
    else:
        parser.print_help()
        exit()
    print(SMARTS)
