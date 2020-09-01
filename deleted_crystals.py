from Bio.PDB import *
import Bio.PDB as bpdb
from Bio.PDB.PDBIO import PDBIO
import argparse
import os
import shutil

from scripts.utils import maestro_writer, cleanup, create_folder
from scripts.configuration_scripts import CONFIGURE

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Automatic RMSD counting for Autodock Vina.')

    parser.add_argument('-p', "--protein", help='input file with protein structure .pdb')
    args = parser.parse_args()

    
    os.system("python3 ./file_separate.py -i %s -f %s" % (args.protein, "crystal"))
    
    sudo_perm="sudo"
    schrodinger_path="/opt/schrodingerfree"
    crystal_path="./crystal"
    crystal_path_pdb="./crystal/pdb"
    GLOBAL_VARIABLES=["/opt/schrodingerfree", "sudo"]
    
    fromaa=-1
    toaa=25
    os.mkdir("./crystal/pdb")

    for cryst in os.listdir("./crystal"):
        if cryst.endswith(".mae"):
            base_prot = os.path.basename(cryst)
            base_name = os.path.splitext(base_prot)[0]
            path_name = os.path.abspath("%s/" % crystal_path + base_name + ".mae")
            path_name_pdb = os.path.abspath("%s/" % crystal_path_pdb +base_name + ".pdb")


            os.system("%s %s/run structconvert.py -imae %s -opdb %s" % (sudo_perm, schrodinger_path, path_name, path_name_pdb))
            print(base_name, path_name_pdb)


            os.system("sudo chmod 777 %s" % (path_name_pdb))
            parser = PDBParser(PERMISSIVE=1) 
            structure = parser.get_structure(base_name, path_name_pdb)
            print(structure.get_id())
            chains=[]
            for model in structure:
                for chain in model:
                    chains.append(chain.get_id())
            #chain.append(model.get_chains().get_id())

            chain_id=chains[0]
            class ResSelect(bpdb.Select):
                def accept_residue(self, res):
                    if res.id[1] >= fromaa and res.id[1] <= toaa and res.parent.id == chain_id:
                        return False
                    else:
                        return True

            io = PDBIO()
            io.set_structure(structure)
            io.save(path_name_pdb, ResSelect())

            os.system("%s %s/run structconvert.py -ipdb %s -omae %s" % (sudo_perm, schrodinger_path, path_name_pdb, os.path.abspath("%s/" % crystal_path_pdb+base_name+".mae")))

            with open(os.path.abspath("%s/" % crystal_path_pdb+base_name+".mae"), "rt") as file:
                lines = file.readlines()
                ind_dots = []
                for i in range(len(lines)):
                    if lines[i] == ' :::\n':
                        ind_dots.append(i)
                ddd = ind_dots[1] + 1
                lines[ddd] = " "+base_name+"\n"

            os.system("sudo chmod 777 " + os.path.abspath("%s/" % crystal_path_pdb+base_name+".mae"))  # TODO

            with open(os.path.abspath("%s/" % crystal_path_pdb+base_name+".mae"), "w") as file:
                for line in lines:
                    file.write(line)

        
            #os.remove(path_name_pdb)
            #os.remove(path_name)

    
    list_crystal_path_pdb=os.listdir(crystal_path_pdb)
    for i in range(len(list_crystal_path_pdb)):
        list_crystal_path_pdb[i]+=" "
    os.system("%s %s/utilities/structcat %s/%s -omae %s" % (GLOBAL_VARIABLES[1], GLOBAL_VARIABLES[0], crystal_path_pdb, (crystal_path_pdb+"/").join(list_crystal_path_pdb), "merged.mae")) 
    





