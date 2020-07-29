#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def separate_ligands(file_path, folder):
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
    import os
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input file with multiple ligands.")
    parser.add_argument("-f", "--folder", help="Working folder inside current directory. Will be created if doesn't exist.")
    args = parser.parse_args()

    separate_ligands(args.input, args.folder)
