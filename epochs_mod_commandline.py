import paradigm_config_mod as tacr_cfg
import sys
sys.path.insert(0, tacr_cfg.shared_func_dir)
import json
import logging
import argparse
import io_mod as i_o
import preprocessing as preproc
import artifact_removal_config as rm_arti_cfg
from os.path import join


def main(subject, subject_fnames, log):
    logging.basicConfig(filename=log, level=logging.DEBUG)

    subject_paradigm_dir = join(tacr_cfg.paradigm_dir, subject)

    for subdir in ['preproc_subdir', 'preproc_plots_subdir', 'epochs_subdir']:
        i_o.check_and_build_subdir(subject_fnames[subdir])

    sss = i_o.preload_raws(subject_paradigm_dir, subject_fnames['sss_paradigm'])

    events, events_baseline = i_o.find_events(sss, stim_channel='STI101')

    filt = preproc.filter_signal(sss, tacr_cfg.l_freq, tacr_cfg.h_freq, tacr_cfg.n_jobs, tacr_cfg.eeg, subject_paradigm_dir,
                                 subject_fnames['eeg_bads'], subject_fnames['preproc_subdir'], subject_fnames['filt_paradigm'])

    if tacr_cfg.preproc_ssp:
        filt_ssp = preproc.ssp_exg(filt, rm_arti_cfg.ssp_params_dict, tacr_cfg.n_jobs, subject_fnames['proj'],
                                   subject_fnames['ssp_topo'], subject_fnames['preproc_plots_subdir'])

    epochs = preproc.generate_epochs(filt_ssp, events_baseline, tacr_cfg.conditions_dicts, tacr_cfg.epochs_parameters_dict,
                                     subject_fnames['epochs_subdir'], subject_fnames['epoch'], tacr_cfg.proc_using_baseline)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-subject', type=str, help='Subject ID')
    parser.add_argument('-log', type=str, help='Logging script file name')
    parser.add_argument('-fnames', type=json.loads, help='Subject file naming information')

    arguments = parser.parse_args()

    main(arguments.subject, arguments.fnames, arguments.log)
