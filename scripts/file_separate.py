#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse


def separate_ligands(file_path, folder):
    """
    Separate .mae file into entries.

    :param str file_path: .mae file to separate
    :param str folder: workspace folder to save separated files

    :var str intro: required intro part to write into each new .mae file
    :var list parts: sections of the file

    :return int error_code:
        1: No input provided
        2: File doesn't exist
    :return list or None titles_file: returns files paths in the same order as in the input (file_path)
    """

    try:
        file = open(file_path).read()
    except TypeError:
        print("No input file!")
        return 1, None
    except FileNotFoundError:
        print("No such file: %s" % file_path)
        return 2, None

    try:
        os.mkdir(folder)
    except FileExistsError:
        print("Directory %s already exists! Continuing..." % folder)

    parts = file.split(' } \n} \n')  # Splits .mae file into separate sections

    intro = parts[0].split("} \n\n")[0]  # First section will also contain intro part, here we also separate it.
    intro = "".join([intro, "} \n"])

    parts[0] = parts[0].split("} \n\n")[1]

    titles_file = []

    for i in range(len(parts) - 1):
        title0 = parts[i].split(" :::")[1].split('\n')[1].strip()  # Suitable descriptor for file name can be found here.
        title1 = title0.split(":")[-1]
        titles_file.append(title1)

        out = open("%s/%s.mae" % (folder, title1), 'w')  # Saving single section with intro.
        out.write(intro)
        out.write(parts[i])
        out.write(" } \n} \n")
        out.close()
    return 0, titles_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Separate .mae file into separate entries. Using id strings as unique filenames.")
    parser.add_argument("-i", "--input", help="input file with multiple ligands")
    parser.add_argument("-f", "--folder", help="working folder inside current directory. Will be created if doesn't exist")
    args = parser.parse_args()

    separate_ligands(args.input, args.folder)
