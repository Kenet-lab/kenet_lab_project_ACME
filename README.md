# Kenet Lab - project ACME
"Academic Code Modularization Endeavor/Expedition"

The entry point for this system is the `<paradigm>_wrapper.py` script.
("paradigm" is replaced according to directory, paradigm)

Once the user has defined relevant paradigm and analysis
parameters/variables in ``paradigm_config_mod``, the wrapper will run
`filenaming_config` for each subject in the wrapper loop.

This script must be run from the corresponding paradigm directory since the paradigm configuration file
is generically imported/aliased as "para_cfg". < Liable to change in future versions! (June 2020)

The paradigm wrapper script will interface with the paradigm and
filenaming configurations, passing the subject's ID, filenaming
dictionary, and relevant logging file.
  1. mne_maxwell
  2. epochs_mod
  3. sensor_tfr
  
  
