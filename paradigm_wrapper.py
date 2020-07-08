import os
import filenaming_config as fname_cfg
import paradigm_config as paradigm_cfg
from mnepy_sss import main as maxwell_main
from epoching import main as epochs_main
from sensor_space_analysis import main as sensor_tfr_main
from pathlib import Path


def subject_unprocessed(subject_filenaming_dict, stage):
    """ true if the subject has not been successfully processed """
    return (not os.path.isfile(subject_filenaming_dict[stage]))


def mark_successful_stage(stage):
    """ produce a sentinel file to indicate successful completion of a stage"""
    Path.touch(stage)


def run_if_needed(function, stage, subject, subject_filenaming_dict, log_name, override=False):
    """ runs the supplied script if necessary"""
    if override or subject_unprocessed(subject_filenaming_dict, stage):
        function(subject, subject_filenaming_dict, log_name)
        mark_successful_stage(stage)


def run_subject(subject, subject_filenaming_dict):
    """ process a single subject"""
    # maxwell filtering script
    run_if_needed(maxwell_main, fname_cfg.Sentinel.MAXWELL, subject, subject_filenaming_dict,
                  fname_cfg.maxwell_script_log_name, override=False)
    # further preprocessing and epochs script
    run_if_needed(epochs_main, fname_cfg.Sentinel.EPOCH, subject, subject_filenaming_dict,
                  fname_cfg.epoched_script_log_name, override=False)
    # sensor space script
    run_if_needed(sensor_tfr_main, fname_cfg.Sentinel.SENSORS_TFR, subject, subject_filenaming_dict,
                  fname_cfg.sensor_space_script_log_name, override=False)


def run_subjects():
    """ process all subjects in the paradigm directory"""
    for subject in os.listdir(paradigm_cfg.paradigm_dir):
        if subject.isnumeric():
            subject_filename_dict = fname_cfg.create_paradigm_subject_mapping(subject)
            run_subject(subject, subject_filename_dict)


if __name__ == "__main__":
    run_subjects()
