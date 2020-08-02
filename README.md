# Workflow maestro_auto_dock 

### README WIP

Workflow to automate calculating RMSD values between protein and ligands in Maestro and Vina.

## Requirements
### Linux
Sudo user is recommended, but not necessary.

### Python 3
%-strings are used, so even older version of Python (before 3.5) should be supported.    
Only standard libraries are used, no special requirements.

### Schrödinger
Working Schrödinger is absolutely necessary, even when using Vina wrapper.

## Flags description:
Maestro wrapper:    

Flag | Full Flag | Description | Default value
-----|-----------|-------------|------------------
-d | --docking | input file from docking, unzipped *_pv.maegz | -
-c | --crystal | input file with crystals | -
-o | --output | output filename | maestro_script.txt
-r | --remove | clear created temp files and folders after finished run | False
-u | --update | update gloabal variables | False


Vina wrapper:    

Flag | Full Flag | Description | Default value
-----|-----------|-------------|------------------
-p | --protein | input file with protein structure .pdb | -
-c | --crystal | input file with crystal | -
-l | --ligand | path to folder with ligands .pdb | -
-o | --output | output file name | vina_maestro_script.txt
-r | --remove | clear created temp files and folders after finished run | False
-u | --update | update gloabal variables | False


## Examples - WIP
Maestro wrapper:    
```python3 maestro_workflow -p -c -l -r```

Vina wrapper:    
```python3 vina_workflow -p -c -l -r```

