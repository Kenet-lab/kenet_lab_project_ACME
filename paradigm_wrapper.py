import filenaming_config as fname_cfg
import paradigm_config as paradigm_cfg
from mnepy_sss import main as maxwell_main
from epoching import main as epochs_main
from sensor_space_analysis import main as sensor_tfr_main
from mne import open_report, Report
from io_helpers import check_and_build_subdir
from os import listdir, walk
import os.path as op


def run_if_needed(function, subject, subject_filenaming_dict, log_name, override=True):
    """ runs the supplied script if necessary"""
    if override:
        function(subject, subject_filenaming_dict, log_name)


def run_subject(subject, subject_filenaming_dict):
    """ process a single subject"""
    # maxwell filtering script
    run_if_needed(maxwell_main, subject, subject_filenaming_dict,
                  fname_cfg.maxwell_script_log_name, override=True)
    # further preprocessing and epochs script
    run_if_needed(epochs_main, subject, subject_filenaming_dict,
                  fname_cfg.epoched_script_log_name, override=True)
    # sensor space script
    run_if_needed(sensor_tfr_main, subject, subject_filenaming_dict,
                  fname_cfg.sensor_space_script_log_name, override=False)


def run_subjects():
    """ process all subjects in the paradigm directory"""
    for subject_folder_path, directory_names, filenames in walk(paradigm_cfg.raw_meg_dir):
        path_identification = op.split(subject_folder_path)
        if 'visit' not in path_identification[1]:
            continue
        #if len(filenames) == 0:
        #    continue

        visit_folder = path_identification[1]
        print(path_identification)
        if len(visit_folder.split('_')[1]) != 8:
            continue
        subject = op.split(path_identification[0])[1]  # split the path again to obtain the subject ID

        print(subject)
        print(visit_folder)

        subject_filename_dict = fname_cfg.create_paradigm_subject_mapping(subject, visit_folder)
        run_subject(subject, subject_filename_dict)


if __name__ == "__main__":
    check_and_build_subdir(paradigm_cfg.reports_dir)
    sensor_report = Report()
    run_subjects()
    sensor_report.save(op.join(paradigm_cfg.reports_dir, paradigm_cfg.sensor_report_fname.replace('h5', 'html')))
