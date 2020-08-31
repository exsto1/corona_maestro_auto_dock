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

from scripts.utils import maestro_writer, cleanup, create_folder
from scripts.configuration_scripts import CONFIGURE

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Automatic RMSD counting for Autodock Vina.')

    parser.add_argument('-p', "--protein", help='input file with protein structure .pdb')
    parser.add_argument('-c', "--crystal", help='input file with crystal')
    parser.add_argument('-l', "--ligand", help='path to folder with ligands .pdb')
    parser.add_argument('-o', "--output", help='output file name', default="vina_maestro_script.txt")
    parser.add_argument("-r", "--remove", help="clear created temp files and folders after finished run; default: True", action="store_true")
    parser.add_argument("-u", "--update", help="update gloabal variables; default: False", action="store_true")

    args = parser.parse_args()

    def main():
        """
        Main function. Creates Maestro script.
        """

        GLOBAL_VARIABLES = CONFIGURE(args.update)  # utils.py

        create_folder(os.path.abspath("./workspace"), True)
        create_folder(os.path.abspath("./workspace/ligand_mae"), True)

        ligand_path = os.path.abspath("./workspace/ligand_mae")
        combined_ligand_filename = os.path.abspath("./workspace/ligs.mae")
        protein_filename = os.path.abspath("./workspace/bialko.mae")
        ligand_protein_filename = os.path.abspath("./workspace/all.mae")
        SMARTS_filename = os.path.abspath("./workspace/SMARTS.txt")
        input_filename = os.path.abspath("./workspace/all-out_complex.mae")

        ligand_files = []
        try:
            ligand_files = os.listdir(args.ligand)
        except FileNotFoundError:
            print("Folder not found %s" % args.ligand)
            parser.print_help()
            exit()

        for file in ligand_files:
            base = os.path.basename(file)
            nazwa = "%s/%s.mae" % (ligand_path, os.path.splitext(base)[0])
            os.system("%s %s/run structconvert.py -ipdb %s %s" % (GLOBAL_VARIABLES[1], GLOBAL_VARIABLES[0], file, nazwa))
        # TODO wyciągnąć nazwy z : jak w file_separate.py
        titles_file = []

        for i in os.listdir(ligand_path):
            temp = open("%s/%s" % (ligand_path, i)).read()
            title0 = temp.split(" :::")[2].split('\n')[1].strip()  # Suitable descriptor for file name can be found here.
            title1 = title0.split(":")[-1]
            titles_file.append(title1)

# TODO #####
        os.system("SCHRODINGER/utilities/structcat %s -omae ./workspace/ligand_mae/ligs.mae" % " ".join("/".join([" ./workspace/ligand_mae/", os.listdir("./workspace/ligand_mae")])))
# TODO #####

        os.system("%s %s/run structconvert.py -ipdb %s %s" % (GLOBAL_VARIABLES[1], GLOBAL_VARIABLES[0], args.protein, protein_filename))

        os.system("%s %s/run gen_smarts.py %s/%s %s" % (GLOBAL_VARIABLES[1], GLOBAL_VARIABLES[0], ligand_path, combined_ligand_filename, SMARTS_filename))

        SMARTS = open(SMARTS_filename).readlines()
        SMARTS = [i.rstrip() for i in SMARTS]

        os.system("%s SCHRODINGER/utilities/structcat -imae %s -imae %s/%s -omae %s" % (GLOBAL_VARIABLES[1], protein_filename, ligand_path, combined_ligand_filename, ligand_protein_filename))  # TODO CONFIGURE???

        os.system("%s %s/run pv_convert.py -mode merge %s" % (GLOBAL_VARIABLES[1], GLOBAL_VARIABLES[0], ligand_protein_filename))

        maestro_writer(args.output, args.crystal, input_filename, titles_file, SMARTS)  # utils.py

        if args.remove:
            paths = [os.path.abspath("./workspace")]  # Folders to clean.
            cleanup(paths)  # utils.py

    main()
    # TODO zmienić nazwy sekcji w połączonym pliku z ligandami .mae
    # TODO imput_filename path check.
