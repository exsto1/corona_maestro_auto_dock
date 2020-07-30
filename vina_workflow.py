"""
Input:

-plik pdb z bialkiem
-pliki pdb z ligandami
-pliki pdb z kryształami

1) Pliki .pdb zamienić na pliki .mae --> $SCHRODINGER/utilities/structconvert -ipdb plik.pdb -omae plik.mae

2) Łączymy wszystkie pliki .mae z ligandami do jednego wspólnego pliku .mae ---> $SCHRODINGER/utilities/structcat -imae lig1.mae -imae lig2.mae ..... -omae ligs.mae

3) Mamy teraz 2 pliki .mae:
	-bialko.mae
        -ligs.mae

4) generujemy SMARTS dla pliku z samymi ligandami: os.system("sudo /opt/schrodingerfree/run gen_smarts.py ./docking/%s.mae SMARTS.txt" % ligs.mae)

5) łączymy bialko.mae z ligs.mae --> $SCHRODINGER/utilities/structcat -imae bialko.mae -imae ligs.mae -omae all_pv.mae

6) zmienić plik aby zawierał kompleksy --> $SCHRODINGER/run pv_convert.py -mode merge all_pv.mae  --> dostaniemy all-out_complex.mae

7) reszta jak w maestro
"""

import argparse
import os

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-p', "--protein", help='an integer for the accumulator')
parser.add_argument('-c', "--crystal", help='an integer for the accumulator')
parser.add_argument('-l', "--ligand", help='an integer for the accumulator')

args = parser.parse_args()

# TODO Check if PATH exists
# TODO Check folders and create
ligand_files = os.listdir(args.ligand)
for file in ligand_files:
    base = os.path.basename(file)
    nazwa = "workspace/ligand_mae/%s.mae" % os.path.splitext(base)[0]  # TODO - ścieżka osobno
    os.system("sudo /opt/schrodingerfree/run structconvert.py -ipdb %s %s" % (file, nazwa))
# TODO wyciągnąć nazwy z : jak w file_separate.py
titles_file = []

for i in os.listdir("workspace/ligand_mae/"):
    temp = open("workspace/ligand_mae/%s" % i).read()
    title0 = temp.split(" :::")[2].split('\n')[1].strip()  # Suitable descriptor for file name can be found here.
    title1 = title0.split(":")[-1]
    titles_file.append(title1)

os.system("SCHRODINGER/utilities/structcat %s -omae ./workspace/ligands/ligs.mae" % " ".join(os.listdir("./workspace/ligand_mae")))

nazwa_bialko = "workspace/bialko.mae"  # TODO ścieżka
os.system("sudo /opt/schrodingerfree/run structconvert.py -ipdb %s %s" % (args.protein, nazwa_bialko))


os.system("sudo /opt/schrodingerfree/run gen_smarts.py ./docking/%s.mae SMARTS.txt" % "ligs.mae")  # TODO ścieżka
SMARTS = open("SMARTS.txt").readlines()
SMARTS = [i.rstrip() for i in SMARTS]

os.system("SCHRODINGER/utilities/structcat -imae bialko.mae -imae ligs.mae -omae all_pv.mae")  # TODO ścieżki

os.system("sudo /opt/schrodingerfree/run pv_convert.py -mode merge all_pv.mae")  # TODO ścieżki

input_file = "all-out_complex.mae"  # TODO ścieżki



output = open(args.output, "w")
output.write('entryimport "%s"\nentryimport "%s"\nshowpanel superimpose\n\n' % (args.crystal, os.path.abspath('/'.join(["./workspace" + input_file]))))

for i in range(len(titles_file)):
    output.write("entrywsincludeonly s_m_title *%s*\n" % '_'.join(titles_file[i].split('_')[:2]))
    output.write("entrywsinclude s_m_title %s\n" % '_'.join(titles_file[i].split('_')[:1]))
    output.write(
        'propertysuperimposesetting  applytoentries=included\nsuperimpose  inplace=false\nsuperimposeset atom.ptype " CA "\nsuperimpose  inplace=true\n')
    output.write('superimposesmarts "%s" \n\n' % SMARTS[i].rstrip())

output.close()
