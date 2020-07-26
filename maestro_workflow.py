#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os

import file_separate


parser = argparse.ArgumentParser()

parser.add_argument("-d", "--docking", help="Input file from docking. Unzipped. *_pv.maegz")
parser.add_argument("-c", "--crystal", help="Input file with crystals.")
parser.add_argument("-o", "--output", help="Output filename.", default="maestro_script.txt")

args = parser.parse_args()

if __name__ == "__main__":
    base=os.path.basename(args.docking)
    unzipped=os.path.splitext(base)[0]+".mae"
    os.system("sudo /opt/schrodingerfree/run structconvert.py -imae %s %s" %(args.docking,unzipped))


    error_code, titles_SMARTS = file_separate.separate_ligands(unzipped, "docking")
    if error_code != 0:
        parser.print_help()
        exit(error_code)

    SMARTS_save = []

    for i in range(1, len(titles_SMARTS)):
        try:
            os.system("python ./gen_smarts.py -i ./docking/%s.mae, -o ./DELETE" % (titles_SMARTS[i]))
            temp = open("./DELETE")
            temp1 = temp.read()
            SMARTS_save.append(temp1)
            temp.close()
        except ValueError:
            print("ERROR: %s" %titles_SMARTS[i])
    os.remove("./DELETE")

    os.system("sudo /opt/schrodingerfree/run pv_convert.py -mode merge %s" %(unzipped))

    input = ""
    for i in os.listdir("./"):
        if unzipped.rstrip("_pv.mae") in i and "out_complex" in i and "maegz" not in i:
            input = i
            break

    if input:
        error_code, titles_file = file_separate.separate_ligands(input, "ligands")
        if error_code != 0:
            parser.print_help()
            exit(error_code)
    else:
        print("File not found - complex.")
        exit()

    files = os.listdir("./ligands")


    output = open(args.output, "w")
    output.write('entryimport "%s"\nentryimport "%s"\nshowpanel superimpose\n\n' %(args.crystal, input))

    for i in range(len(titles_file)):
        output.write("entryincludeonly s_m_title *%s*\n" % '_'.join(titles_file[i].split('_')[:2]))
        output.write("entryinclude s_m_title %s\n" % '_'.join(titles_file[i].split('_')[:1]))
        output.write('propertysuperimposesetting  applytoentries=included\nsuperimpose  inplace=false\nsuperimposeset atom.ptype " CA "\nsuperimpose  inplace=true')
        output.write('uperimposesmarts "%s"\n\n' % SMARTS_save[i])

    output.close()
