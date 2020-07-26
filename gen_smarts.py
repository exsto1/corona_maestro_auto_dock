#Name: Project Table:Generate SMARTS
#Command: pythonrun gen_smarts.add_smarts
__doc__ = """
Creates a (non-canonical) SMARTS string property for each structure.

When run from Maestro, selected entries in the project table are used and the
SMARTS pattern is added back to the project table.

When run from outside Maestro, a SMARTS pattern is generated for each input
structure in the file and this is written to the an output file.

Structures that are larger than 200 atoms are skipped and no SMARTS pattern is 
generated.

Copyright Schrodinger, LLC. All rights reserved.
"""

# Used by KNIME

try:
    from schrodinger import maestro
except ImportError:
    maestro = None

from schrodinger import structure
from schrodinger.structutils import analyze
import sys, os
import argparse
from schrodinger.utils import fileutils
from schrodinger.utils import log

# Check whether SCHRODINGER_PYTHON_DEBUG is set for debugging:
DEBUG = (log.get_environ_log_level() <= log.DEBUG)
logger = log.get_output_logger('gen_smarts.py')

# This is the name of the new property which will be created in the project
# table.
SMARTS_PROPERTY_NAME = 's_user_SMARTS'
# The following is the maximum number of atoms we will attempt to generate
# a SMARTS expression for.
MAX_NUM_ATOMS = 200


def gen_smarts(st):
    """
    Generate and return a SMARTS pattern for the input structure st.
    """
    this_smarts = analyze.generate_smarts_canvas(
        st, honor_maestro_prefs=(maestro is not None))
    # FIXME These are likely no longer needed with Canvas SMILES generation:
    this_smarts = this_smarts.replace("-0", "")
    this_smarts = this_smarts.replace("+X3", "X3+")
    this_smarts = this_smarts.replace("+X4", "X4+")
    return this_smarts


def add_smarts():
    """
    This is the function which is actually called from Maestro
    """

    # Get the project table from Maestro
    pt = maestro.project_table_get()

    if len(pt.selected_rows) == 0:
        maestro.warning("There are no entries selected in order to generate "
                        "SMARTS. Select some entries in the project and try "
                        "again")
        return

    for irow in pt.selected_rows:
        st = irow.structure
        if st.atom_total <= MAX_NUM_ATOMS:
            irow[SMARTS_PROPERTY_NAME] = gen_smarts(st)

    pt.refreshTable()


if __name__ == '__main__':
    # Running from the command line:

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        'input_file',
        metavar='<INPUT_FILENAME>',
        help='Structure file in Maestro, SD or Mol2 format')
    parser.add_argument(
        'out_file',
        metavar='<OUTPUT_FILENAME>',
        help='The file the SMARTS patterns are to be written to')

    options = parser.parse_args()

    fileutils.force_remove(options.out_file)

    outputFile = open(options.out_file, 'w+')

    for count, st in enumerate(structure.StructureReader(options.input_file)):
        this_smarts = gen_smarts(st)
        logger.debug("Structure #%i" % count)
        outputFile.write(this_smarts)
        outputFile.write("\n")

    outputFile.close()
    logger.info("Done. Written file: %s" % options.out_file)
