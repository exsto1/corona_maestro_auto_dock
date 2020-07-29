def SMARTS_extract():
    error_code, titles_SMARTS = separate_ligands(unzipped, "docking")  # Separate entries
    if error_code != 0:
        parser.print_help()
        exit(error_code)

    # From each file extract SMARTS to temporary file and store value in a list
    SMARTS_save = []

    for i in range(1, len(titles_SMARTS)):
        try:
            os.system(
                "sudo /opt/schrodingerfree/run gen_smarts.py ./docking/%s.mae ./workspace/DELETE" % titles_SMARTS[i])
            temp = open("./workspace/DELETE")
            temp1 = temp.read()
            SMARTS_save.append(temp1)
            temp.close()
        except ValueError:
            print("ERROR: %s" % titles_SMARTS[i])
    os.remove("./workspace/DELETE")
    return SMARTS_save


if __name__ == "__main__":
    import os
    import argparse

    # TODO FINISH IMPLEMENTING - RENAME VARIABLES, ADD ARGPARSE, RETURN, ETC...
