# Kenet Lab - project ACME
"Academic Code Modularization Endeavor/Expedition"

The entry point for this system is the `paradigm_wrapper.py` script.

Once the user has defined relevant paradigm and analysis
parameters/variables in ``paradigm_config_mod``, they must run
`filenaming_config` to create all filenames for input/output
throughout the pipeline.

The paradigm wrapper script will interface with the paradigm and
filenaming configurations, passing the subject's ID, filenaming
dictionary, and relevant logging file via command line arguments
  1. mne_maxwell
  2. epochs_mod
  3. sensor_tfr
