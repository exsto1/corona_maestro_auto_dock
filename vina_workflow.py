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
    parser.add_argument("-r", "--remove", help="clear created temp files and folders after finished run; default: True", action="store_true") # TODO
    parser.add_argument("-u", "--update", help="update gloabal variables; default: False", action="store_true")
    parser.add_argument("-s", "--save", help="save workspace folder", default="")  # TODO
    ###
    parser.add_argument("-fr", "--fromaa", help="Number of aa to be removed", default=-1)
    parser.add_argument("-to", "--toaa", help="Number of aa to be removed", default=0)
    ###

    args = parser.parse_args()

###
    def pdb_to_mae(input_file, output_path, schrodinger_path, sudo_perm, output_filename=None):  # konwersja pliku z białkiem z .pdb do .mae. zmiana pliku .mae tak aby nazwa pojawiała się w panelu maestro
        if not output_filename:
            base_prot = os.path.basename(input_file)
            base_name = os.path.splitext(base_prot)[0]
            path_name = os.path.abspath("%s/" % output_path + base_name + ".mae")

        os.system("%s %s/run structconvert.py -ipdb %s %s" % (sudo_perm, schrodinger_path, input_file, path_name))  # change to .mae

        with open(path_name, "rt") as file:
            lines = file.readlines()
            ind_dots = []
            for i in range(len(lines)):
                if lines[i] == ' :::\n':
                    ind_dots.append(i)
            ddd = ind_dots[1] + 1
            lines[ddd] = base_name

        # os.system("sudo chmod 777 " + path_name)  # TODO

        with open(path_name, "w") as file:
            for line in lines:
                file.write(line)

        return path_name, base_name
###

    def main():
        """
        Main function. Creates Maestro script.
        """

        GLOBAL_VARIABLES = CONFIGURE(args.update)  # configuration_scripts.py

        ligand_main_directory = os.path.abspath("./workspace/ligands")
        ligand_mae_path = os.path.abspath("./workspace/ligand_mae")
        combined_ligand_filename = os.path.abspath("./workspace/ligands/ligs.mae")
        preprocessed_ligand_path = os.path.abspath("./workspace/ligands/preprocessed_ligands")
        # ligand_protein_filename = os.path.abspath("./workspace/all.mae")

        protein_original_path = os.path.abspath("./workspace/proteins")
        # protein_filename = os.path.abspath("bialko.mae")

        # complex_input_filename = os.path.abspath("./workspace/complex/all-out_complex.mae")
        complex_original_path = os.path.abspath("./workspace/complex/original")
        complex_deleted_path = os.path.abspath("./workspace/complex/deleted")

        SMARTS_filename = os.path.abspath("./workspace/SMARTS.txt")

        create_folder(os.path.abspath("./workspace"), True)
        create_folder(os.path.abspath(ligand_main_directory), False)
        create_folder(os.path.abspath(ligand_mae_path), False)
        create_folder(os.path.abspath(preprocessed_ligand_path), False)
        create_folder(os.path.abspath(protein_original_path), False)
        create_folder(os.path.abspath(complex_deleted_path), False)
        create_folder(os.path.abspath(complex_original_path), False)

        """
        workspace
            | SMARTS.txt
            ligands
                | ligs.mae
                ligand_mae
                    | *.mae (from pdb)
                preprocessed_lignads
                    | preprocessed_ligands.pdb
            proteins
                | protein_input.mae
                | protein_deleted.mae
            complex
                original  # not-modified
                    | *.pv (maestro)
                    | *.out_complex
                deleted
                    | *.pv (maestro)
                    | *.out_complex
        """


        ligand_files = []
        try:
            ligand_files = os.listdir(args.ligand)
        except FileNotFoundError:
            print("Folder not found %s" % args.ligand)
            parser.print_help()
            exit()

        # for file in ligand_files:
        #     base = os.path.basename(file)
        #     nazwa = "%s/%s.mae" % (ligand_path, os.path.splitext(base)[0])
        #     os.system("%s %s/run structconvert.py -ipdb %s %s" % (GLOBAL_VARIABLES[1], GLOBAL_VARIABLES[0], file, nazwa))
        # # TODO wyciągnąć nazwy z : jak w file_separate.py
        # titles_file = []

        # for i in os.listdir(ligand_path):
        #     temp = open("%s/%s" % (ligand_path, i)).read()
        #     title0 = temp.split(" :::")[2].split('\n')[1].strip()  # Suitable descriptor for file name can be found here.
        #     title1 = title0.split(":")[-1]
        #     titles_file.append(title1)

        titles_file = []
        for file in ligand_files:
            temp, base_lig = pdb_to_mae(file, ligand_mae_path, GLOBAL_VARIABLES[0], GLOBAL_VARIABLES[1])
            titles_file.append(base_lig)

# TODO #####
        os.system("SCHRODINGER/utilities/structcat %s -omae ./workspace/ligand_mae/ligs.mae" % " ".join("/".join([" ./workspace/ligand_mae/", os.listdir("./workspace/ligand_mae")])))
# TODO #####

        os.system("%s %s/run gen_smarts.py %s/%s %s" % (GLOBAL_VARIABLES[1], GLOBAL_VARIABLES[0], ligand_mae_path, combined_ligand_filename, SMARTS_filename))

        SMARTS = open(SMARTS_filename).readlines()
        SMARTS = [i.rstrip() for i in SMARTS]

        # os.system("%s %s/run structconvert.py -ipdb %s %s" % (GLOBAL_VARIABLES[1], GLOBAL_VARIABLES[0], args.protein, protein_filename))
        ###
        protein_path, protein_base = pdb_to_mae(args.protein, protein_original_path, GLOBAL_VARIABLES[0], GLOBAL_VARIABLES[1])
        ###

        ### łączenie białka z ligandami i usuwanie albo i nie

        # pose_viewer file and complex file for name_prot
        os.system("%s %s/utilities/structcat -imae %s -imae %s -omae %s_pv.mae" % (GLOBAL_VARIABLES[1], GLOBAL_VARIABLES[0], protein_path, combined_ligand_filename, os.path.abspath(complex_original_path + "/" + protein_base)))
        os.system("%s %s/run pv_convert.py -mode merge %s_pv.mae" % (GLOBAL_VARIABLES[1], GLOBAL_VARIABLES[0], os.path.abspath(complex_original_path + "/" + protein_base)))  # TODO ścieżki
        input_file = os.path.abspath(complex_original_path + "/" + protein_base) + "-out_complex.mae"

        # pose_viewer file and complex file for name_prot2
        if args.toaa != 0:
            protein_base_deleted = protein_base + "_deleted"
            protein_path_deleted = os.path.abspath("workspace/" + protein_base_deleted + ".mae")

            os.system("%s %s/run delete_atoms.py -asl \"res.num %s-%s\" %s %s" % (GLOBAL_VARIABLES[1], GLOBAL_VARIABLES[0], args.fromaa, args.toaa, protein_path, protein_path_deleted))
            os.system("%s %s/utilities/structcat -imae %s -imae %s -omae %s_pv.mae" % (GLOBAL_VARIABLES[1], GLOBAL_VARIABLES[0], protein_path_deleted, combined_ligand_filename, os.path.abspath(complex_deleted_path + "/" + protein_base_deleted)))
            os.system("%s %s/run pv_convert.py -mode merge %s_pv.mae" % (GLOBAL_VARIABLES[1], GLOBAL_VARIABLES[0], os.path.abspath(complex_deleted_path + "/" + protein_base_deleted)))
            input_file = os.path.abspath(complex_deleted_path + "/" + protein_base_deleted + "-out_complex.mae")

        maestro_writer(args.output, args.crystal, input_file, titles_file, SMARTS)  # utils.py

        if args.remove:
            paths = [os.path.abspath("./workspace")]  # Folders to clean.
            cleanup(paths)  # utils.py

    main()
    # TODO zmienić nazwy sekcji w połączonym pliku z ligandami .mae
    # TODO imput_filename path check.
