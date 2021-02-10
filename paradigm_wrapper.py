import os
import filenaming_config as fname_cfg
import paradigm_config as paradigm_cfg
from mnepy_sss import main as maxwell_main
from epoching import main as epochs_main
from sensor_space_analysis import main as sensor_tfr_main


def run_if_needed(function, subject, subject_filenaming_dict, log_name, override=True):
    """ runs the supplied script if necessary"""
    if override:
        function(subject, subject_filenaming_dict, log_name)


def run_subject(subject, subject_filenaming_dict):
    """ process a single subject"""
    # maxwell filtering script
    run_if_needed(maxwell_main, subject, subject_filenaming_dict,
                  fname_cfg.maxwell_script_log_name)
    # further preprocessing and epochs script
    run_if_needed(epochs_main, subject, subject_filenaming_dict,
                  fname_cfg.epoched_script_log_name)
    # sensor space script
    run_if_needed(sensor_tfr_main, subject, subject_filenaming_dict,
                  fname_cfg.sensor_space_script_log_name)


def run_subjects():
    """ process all subjects in the paradigm directory"""
    for subject in os.listdir(paradigm_cfg.paradigm_dir):
        if subject.isnumeric():
            subject_filename_dict = fname_cfg.create_paradigm_subject_mapping(subject)
            run_subject(subject, subject_filename_dict)


if __name__ == "__main__":
    run_subjects()
