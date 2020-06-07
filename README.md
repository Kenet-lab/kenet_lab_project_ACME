# kenet_lab_project_ACME
academic code modularization endeavor/expedition

These scripts serve two purposes, the first of which is to procedurally pre-process data parameterized according 
to a study's paradigm, and perform general analyses on it. The second are sectioned, shared functions that one day aspire
to be wholly modular.

Once the user has defined relevant paradigm and analysis parameters/variables in paradigm_config_mod, they must run filenaming_config to create all filenames for input/output throughout the pipeline

The paradigm wrapper script will interface with the paradigm and filenaming configurations, passing the subject's ID, filenaming dictionary, and relevant logging file via command line arguments
  1. mne_maxwell
  2. epochs_mod
  3. sensor_tfr
