import paradigm_config as para_cfg
import logging
import io_helpers as i_o
import preprocessing as preproc
import artifact_removal_config as rm_arti_cfg
from os.path import join, exists
import os
import fnmatch
from mne.io import read_raw_fif as rrf
from mne import find_events


def main(subject, subject_fnames, log):
    logging.basicConfig(filename=log, level=logging.DEBUG)

    subject_paradigm_dir = join(para_cfg.paradigm_dir, subject)

    for subdir in ['preproc_subdir', 'preproc_plots_subdir', 'epochs_subdir']:
        i_o.check_and_build_subdir(subject_fnames[subdir])
    
    if not exists(join(subject_fnames['preproc_subdir'], subject_fnames['sss_paradigm'])):
        return
    if exists(join(subject_fnames['preproc_subdir'], subject_fnames['filt_paradigm'])):
        return
    
    sssd_data = i_o.preload_raws(subject_fnames['preproc_subdir'], subject_fnames['sss_paradigm'])[0]
    
    events, events_differential_corrected = i_o.find_events(sssd_data, 'STI101', para_cfg.paradigm, para_cfg.epoch_dur)
    
    filt = preproc.filter_signal(sssd_data, para_cfg.l_freq, para_cfg.h_freq, para_cfg.n_jobs, subject_paradigm_dir,
                                 subject_fnames['eeg_bads'], subject_fnames['preproc_subdir'], subject_fnames['filt_paradigm'],
                                 para_cfg.epochs_parameters_dict)
    
    if para_cfg.preproc_ssp:
        raw_sss_filt_ssp = preproc.ssp_exg(filt, rm_arti_cfg.ssp_dict, para_cfg.n_jobs, subject_fnames['proj'],
                                       subject_fnames['preproc_subdir'], subject_fnames['ssp_topo'], subject_fnames['preproc_plots_subdir'])
    

    preproc.generate_epochs(raw_sss_filt_ssp, events, para_cfg.conditions_dicts,
                            para_cfg.epochs_parameters_dict, subject_fnames['epochs_subdir'], subject_fnames['epoch'])
    
