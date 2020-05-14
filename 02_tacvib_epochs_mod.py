from os.path import join
from io_mod import *
from preprocessing import *
from tacvib_config_mod import *
import logging

logging.basicConfig(filename=epoching_script_log_name, level=logging.DEBUG)
for subject in get_subject_ids(get_subjects(paradigm_dir)):
    subject_paradigm_dir = join(paradigm_dir, subject) # locate subject's corresponding paradigm directory

    replace_dict = {'subject': subject} # format subject subdirectories and filenames accordingly
    subject_artifact_eval_subdir, subject_preproc_subdir, subject_sss_pattern, eeg_bads_fname, proj_fname = \
        format_variable_names(replace_dict, artifact_eval_subdir, preproc_subdir, sss_pattern, eeg_bad_channel_pattern, proj_pattern)

    # load raw files
    raw = preload_raws(subject_paradigm_dir, subject_sss_pattern, concat=True)
    # find events
    events, events_baseline = find_events(raw, stim_channel='STI101')

    # do pre-processing
    raw_filt = filter_signal(raw, l_freq, h_freq, n_jobs, eeg, subject_paradigm_dir, subject, eeg_bads_fname)
    if preproc_ssp:
        raw_filt = ssp_exg(raw_filt, ssp_params_dict, n_jobs,
                           proj_fname, subject_preproc_subdir, ssp_topo_pattern, subject_artifact_eval_subdir)
    epochs = generate_epochs(raw, events_baseline, conditions_dicts, epochs_parameters_dict, subject_preproc_subdir,
                             epoch_pattern, proc_using_baseline)
