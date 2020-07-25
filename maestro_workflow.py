import argparse
import os

import file_separate


parser = argparse.ArgumentParser()

parser.add_argument("-i", "--input", help="Input file with multiple ligands.")
parser.add_argument("-d", "--docking", help="Input file from docking. Unzipped. *_pv.maegz")
parser.add_argument("-c", "--crystal", help="Input file with crystals.")
parser.add_argument("-o", "--output", help="Output filename.", default="maestro_script.txt")

args = parser.parse_args()

if __name__ == "__main__":
    error_code, titles_file = file_separate.separate_ligands(args.input)
    if error_code != 0:
        parser.print_help()
        exit(error_code)

    files = os.listdir("./ligands")

    SMARTS_path = "SMARTS.txt"

    os.system("python ./gen_smarts.py -i %s, -o %s" % (args.docking, {SMARTS_path}))

    SMARTS = open(SMARTS_path).readlines()[1:]
    SMARTS = [i.rstrip() for i in SMARTS]

    output = open(args.output, "w")
    output.write('entryimport "%s"\nentryimport "%s"\nshowpanel superimpose\n\n' %(args.crystal, args.input))

    for i in range(len(titles_file)):
        output.write("entryincludeonly s_m_title *%s*\n" % '_'.join(titles_file[i].split('_')[:2]))
        output.write("entryinclude s_m_title %s\n" % '_'.join(titles_file[i].split('_')[:1]))
        output.write('propertysuperimposesetting  applytoentries=included\nsuperimpose  inplace=false\nsuperimposeset atom.ptype " CA "\nsuperimpose  inplace=true')
        output.write('uperimposesmarts "%s"\n\n' % SMARTS[i])

    output.close()
