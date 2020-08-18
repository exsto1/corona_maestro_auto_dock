
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
parser.add_argument("-a", "--aa", help="Number of aa to be removed", default=0) 
#zdecydować czy podawać pozycje od-do aa do wycięcia, czy tylko jedną pozycję aminokwasu do której wycinamy białko (licząc od N-końca) 

args = parser.parse_args()

# TODO Check if PATH exists
# TODO Check folders and create
ligand_files = os.listdir(args.ligand)
for i in range(len(ligand_files)):
    ligand_files[i]=args.ligand+"/"+ligand_files[i]

for file in ligand_files:
    
    with open(file, "rt") as file1:
        lines = file1.readlines()
        base=os.path.basename(file)
        zm=os.path.splitext(base)[0]
        first=lines[0].split()[2]
        if first=="XXXX":
            lines[0] = lines[0].replace('XXXX', zm)
    file1.close()

    if first=="XXXX":
        with open(file, "w") as file1:
            for line in lines:
                file1.write(line)
        

        file1.close()
    
    base = os.path.basename(file)
    #print(base)
    nazwa = "workspace/ligand_mae/%s.mae" % os.path.splitext(base)[0]  # TODO - ścieżka osobno
    os.system("sudo /opt/schrodingerfree/run structconvert.py -ipdb %s -omae %s" % (file, nazwa))
# TODO wyciągnąć nazwy z : jak w file_separate.py
titles_file = []

for i in os.listdir("workspace/ligand_mae/"):
    print("/workspace/ligand_mae/"+i)
    with open("workspace/ligand_mae/"+i, "rt") as file:
        lines = file.readlines()
        l=lines[13].rstrip()
        if l==" \"\"":
            base=os.path.basename(i)
            zm=os.path.splitext(base)[0]
            lines[13] = lines[13].replace('""', zm )
            print(lines[13])
    file.close()
    if l==" \"\"":
        os.system("sudo chmod 777 "+"workspace/ligand_mae/"+i)
        with open("workspace/ligand_mae/"+i, "w") as file:
            for line in lines:
                file.write(line)
        

        file.close()
    temp = open("workspace/ligand_mae/%s" % i).read()
    title0 = temp.split(" :::")[2].split('\n')[1].strip()  # Suitable descriptor for file name can be found here.
    title1 = title0.split(":")[-1]
    titles_file.append(title1)

print(titles_file)
print(" ./workspace/ligand_mae".join(os.listdir("./workspace/ligand_mae")))
os.system("sudo /opt/schrodingerfree/utilities/structcat ./workspace/ligand_mae/%s -omae ./workspace/ligands/ligs.mae" % " ./workspace/ligand_mae/".join(os.listdir("./workspace/ligand_mae")))


base_prot=os.path.basename(args.protein)
name_prot=os.path.splitext(base_prot)[0]
nazwa_bialko = "workspace/" +name_prot+ ".mae"  # TODO ścieżka
os.system("sudo /opt/schrodingerfree/run structconvert.py -ipdb %s %s" % (args.protein, nazwa_bialko))


os.system("sudo /opt/schrodingerfree/run gen_smarts.py %s SMARTS.txt" % "./workspace/ligands/ligs.mae")  # TODO ścieżka
SMARTS = open("SMARTS.txt").readlines()
SMARTS = [i.rstrip() for i in SMARTS]

os.system("sudo /opt/schrodingerfree/utilities/structcat -imae workspace/bialko.mae -imae ./workspace/ligands/ligs.mae -omae all_pv.mae")  # TODO ścieżki

os.system("sudo /opt/schrodingerfree/run pv_convert.py -mode merge all_pv.mae")  # TODO ścieżki

input_file = "all-out_complex.mae"  # TODO ścieżki



output = open("skrypt_vina.cmd", "w")
output.write('entryimport "%s"\nentryimport "%s"\nshowpanel superimpose\n\n' % (args.crystal, os.path.abspath('/'.join(["./workspace/" + input_file]))))
output.write("entrygroupsettitle \"%s\" \"%s\"\n" % (input_file.split(".")[0], name_prot))

for i in range(len(titles_file)):
    output.write("entrywsincludeonly s_m_title *%s*\n" % '_'.join(titles_file[i].split('_')[:2]))
    output.write("entrywsinclude s_m_title %s\n" % titles_file[i].split('_')[1])
    output.write("workspaceselectionreplace res.n -1-%s\ndelete atom.selected allowemptyentry=true\n" % args.aa)
    output.write(
        'propertysuperimposesetting  applytoentries=included\nsuperimpose  inplace=false\nsuperimposeset atom.ptype " CA "\nsuperimpose  inplace=true\n')
    output.write('superimposesmarts "%s" \n\n' % SMARTS[i].rstrip())

output.close()
