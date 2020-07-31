import os


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
            for i in os.listdir(path):
                os.remove("%s/%s" % (path, i))
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
        for file in os.listdir(path):
            os.remove('/'.join([path, file]))
        os.rmdir(path)
