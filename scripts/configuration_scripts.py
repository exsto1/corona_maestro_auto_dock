import os


def CONFIGURE(update=False):
    """
    Set up global variables.

    :param bool update: update global variables mode

    :return list settings_variables: list of global paths specified by the user during first usage

    :key 0: PATH to schrodinger
    """

    CONF_path = os.path.abspath("./scripts/CONFIGURE.txt")

    settings_file = open(CONF_path)
    settings = settings_file.readlines()
    settings_file.close()
    settings_description = [i.lstrip("# ") for i in settings if i[0] == "#"]
    settings_variables = [i.lstrip("V ") for i in settings if i[0] == "V"]

    if not update:
        overwrite = False
        for i in range(len(settings_variables)):
            if not settings_variables[i]:
                settings_variables[i] = os.path.abspath(input(settings_description[i]))
                overwrite = True
    else:
        overwrite = True
        print("Reconfigure global parameters. Leave blank to skip setting.")
        for i in range(len(settings_variables)):
            temp = input(settings_description[i])
            if temp:
                settings_variables[i] = os.path.abspath(temp)

    if overwrite:
        settings_file = open(CONF_path, "w")
        for i in range(len(settings_variables)):
            settings_file.write("# %s \n" % settings_description[i])
            settings_file.write("V %s \n" % settings_variables[i])
        settings_file.close()

    # Special configurations below:
    settings_variables[1] = sudo_perm_config(settings_variables[1])  # Sudo param

    return settings_variables


def sudo_perm_config(state):
    if "t" in state.lower():
        return "sudo"
    else:
        return ""
