import os
import sys
import subprocess
import paradigm_config_mod as paradigm_cfg
sys.path.insert(0, paradigm_cfg.shared_func_dir)
import filenaming_config as fname_cfg


def subject_already_processed(subject_filenaming_dict):
    # loop through subject's filenaming dictionary, if files already exist - return True
    already_processed = False
    for _, subject_file in subject_filenaming_dict.items():
        if os.path.isfile(subject_file):
            already_processed = True
    return already_processed


subjects_filenames_dicts = fname_cfg.subjects_filenames_dicts
for subject in subjects_filenames_dicts.keys(): # loop through paradigm directory, subject-by-subject

    subject_filenaming_dict = subjects_filenames_dicts[subject]
    if subject_already_processed(subject_filenaming_dict):
        continue
    # maxwell filtering script
    sss_cmd = f"python mne_maxwell_commandline.py -subject {subject} -fnames {subject_filenaming_dict} -log {fname_cfg.maxwell_script_log_name}"
    sss_out = subprocess.check_output(sss_cmd)

    # further preprocessing + epoch script
    epo_cmd = f"python epochs_mod_commandline.py -subject {subject} -fnames {subject_filenaming_dict} -log {fname_cfg.epoched_script_log_name}"
    epo_out = subprocess.check_output(epo_cmd)

    # sensor space script
    sensor_cmd = f"python sensor_tfr_commandline.py -subject {subject} -fnames {subject_filenaming_dict} -log {fname_cfg.sensor_space_script_log_name}"
    sensor_out = subprocess.check_output(sensor_cmd)
