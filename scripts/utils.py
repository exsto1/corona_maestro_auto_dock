import os
import shutil


def create_folder(path, remove=False):
    """
    Creates folder for temporary files, deleting old files to avoid confilcts.

    :param str path: path to folder
    :param bool remove: remove content of the folder if exists
    """

    try:
        os.mkdir(path)  # Folder for temporary files
    except FileExistsError:
        if remove:
            print("%s already exists, cleaning old files..." % path)  # ...to avoid possible FileExistsError conflicts.
            shutil.rmtree(path)
            os.mkdir(path)
        else:
            print("%s already exists, continuing..." % path)


def maestro_writer(output_file, crystal_file, input_file, titles_file, SMARTS):
    """
    Writes maestro script to output file.

    :param str output_file: output maestro script filaname
    :param str crystal_file: path to file with crystal
    :param str input_file: path to file with complexes
    :param list titles_file: list with ligand titles in order as in combined file
    :param list SMARTS: list of SMARTS in the same order as in titles_file
    """

    output = open(output_file, "w")
    output.write('entryimport "%s"\nentryimport "%s"\nshowpanel superimpose\n\n' % (os.path.abspath(crystal_file), os.path.abspath(input_file)))

    for i in range(len(titles_file)):
        output.write("entrywsincludeonly s_m_title *%s*\n" % '_'.join(titles_file[i].split('_')[:2]))
        output.write("entrywsinclude s_m_title %s\n" % '_'.join(titles_file[i].split('_')[:1]))
        output.write('propertysuperimposesetting  applytoentries=included\nsuperimpose  inplace=false\nsuperimposeset atom.ptype " CA "\nsuperimpose  inplace=true\n')
        output.write('superimposesmarts "%s" \n\n' % SMARTS[i].rstrip())

    output.close()


def cleanup(paths):
    """
    Cleans files and folders after finished run.

    :param list paths: list of paths to clean
    """

    for path in paths:
        shutil.rmtree(path)


def CONFIGURE(update=False):
    """
    Set up global variables.

    :param bool update: update global variables mode

    :return list settings_variables: list of global paths specified by the user during first usage

    :key 0: PATH to schrodinger
    """

    CONF_path = "./scripts/CONFIGURE.txt"
    settings_file = open(CONF_path)
    settings = settings_file.readlines()
    settings_file.close()
    settings_description = [i.lstrip("# ") for i in settings if i[0] == "#"]
    settings_variables = [i.lstrip("V ") for i in settings if i[0] == "V"]

    if not update:
        overwrite = False
        for i in range(len(settings_variables)):
            if not settings_variables[i]:
                settings_variables[i] = input(settings_description[i])
                overwrite = True
    else:
        overwrite = True
        print("Reconfigure global parameters. Leave blank to skip setting.")
        for i in range(len(settings_variables)):
            temp = input(settings_description[i])
            if temp:
                settings_variables[i] = temp

    if overwrite:
        settings_file = open(CONF_path, "w")
        for i in range(len(settings_variables)):
            settings_file.write("# %s \n" % settings_description[i])
            settings_file.write("V %s \n" % settings_variables[i])

    return settings_variables
