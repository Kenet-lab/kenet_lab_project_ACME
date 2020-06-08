import os
import sys
from pathlib import Path

import io_mod as i_o
import filenaming_config as fname_cfg
import paradigm_config_mod as paradigm_cfg
from mne_maxwell_commandline import main as MNE_MAX_main
from epochs_mod_commandline import main as EPO_main
from sensor_tfr_commandline import main as SENSORS_TFR_main

# DPK - why do you need this?  Is this preferable to the PYTHONPATH
#       environment variable?
sys.path.insert(0, paradigm_cfg.shared_func_dir)


def subject_unprocessed(subject_filenaming_dict, stage):
    """True if the subject has not been successfully processed."""
    return (not os.path.isfile(subject_filenaming_dict[stage]))


def markSuccessfulStage(stage):
    """Produce a sentinal file to indicate successful completion of a stage."""
    Path.touch(stage)


def runIfNeeded(function, stage, subject, subject_filenaming_dict, log_name,
                override=False):
    """Runs the supplied script if necessary."""
    if override or subject_unprocessed(subject_filenaming_dict, stage):
        function(subject, subject_filenaming_dict, log_name)
        markSuccessfulStage(stage)


def runSubject(subject, subject_filenaming_dict):
    "Process a single subject."

    # maxwell filtering script
    runIfNeeded(
        MNE_MAX_main,
        fname_cfg.Sentinel.MAXWELL,
        subject,
        subject_filenaming_dict,
        fname_cfg.maxwell_script_log_name,
        override=False,
    )

    # further preprocessing + epoch script
    runIfNeeded(
        EPO_main,
        fname_cfg.Sentinel.EPOCH,
        subject,
        subject_filenaming_dict,
        fname_cfg.epoched_script_log_name,
        override=False,
    )

    # sensor space script
    runIfNeeded(
        SENSORS_TFR_main,
        fname_cfg.Sentinel.SENSORS_TFR,
        subject,
        subject_filenaming_dict,
        fname_cfg.sensor_space_script_log_name,
        override=False,
    )


def runSubjects():
    "Process all subjects in the paradigm directory."
    for subject in i_o.get_subject_ids(i_o.get_subjects()):
        subject_filename_dict = fname_cfg.create_paradigm_subjects_mapping(
            subject)
        runSubject(subject, subject_filename_dict)


if __name__ == "__main__":
    runSubjects()
