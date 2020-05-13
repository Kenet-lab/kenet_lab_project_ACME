import mne
import numpy as np
import scipy
import subprocess
import shlex
import logging

from visuals import *
from io_mod import *

def apply_bad_channels_eeg(raw, loc, eeg_bads_fname): # read, and add bad EEG channels to raw data
    replace_dict = {'subject': get_subject_id_from_data(raw)}
    eeg_bads_fname = format_variable_names(replace_dict, eeg_bads_fname)
    eeg_bads = read_bad_channels_eeg(loc, eeg_bads_fname)
    raw.info['bads'] += eeg_bads
    return raw

def apply_notch_filter(raw, n_jobs, loc, eeg_bads_fname):
    linefreq = raw.info['line_freq'] # notch filter line frequency
    raw = apply_bad_channels_eeg(raw, loc, eeg_bads_fname)
    for harmonic_num in [1, 2, 3]: # notch filter its second and third harmonics
        notch_freq = linefreq * harmonic_num
        raw.notch_filter(np.arange(notch_freq, 241, notch_freq), picks=['eeg'], n_jobs=n_jobs)
    return raw

def filter_signal(raw, l_freq, h_freq, n_jobs, eeg, save_loc, subject, eeg_bads_fname):
    """
    :param raw: signal to filter
    :param l_freq: low cut frequency
    :param h_freq: high cut frequency
    :param ch_type: used for applying a notch filter to EEG channels (Elekta software notch filters MEG channels)
    :param n_jobs: job control
    :return: filtered signal
    """
    raw.load_data()
    eeg_status = check_eeg_availability(raw)
    if eeg and eeg_status: # explicitly check if EEG channels are present
        raw = apply_notch_filter(raw, n_jobs, save_loc, eeg_bads_fname)
    raw.filter(l_freq=l_freq, h_freq=h_freq, n_jobs=n_jobs)
    return raw


def generate_head_origin(info, subject_meg_dir, head_origin_fname): # calculate, save head origin coordinates
    """
    :param info: MNE Info object
    :return: array -> [x y z] in millimeters!
    """
    all_coords = mne.bem.fit_sphere_to_headshape(info, units='mm')
    head_origin = all_coords[1]
    save_head_origin(head_origin, subject_meg_dir, head_origin_fname)
    return head_origin

def ssp_exg(raw, ssp_params_dict, n_jobs, proj_fname, proj_save_loc, ssp_topo_pattern, plot_save_loc):
    """
    perform artifact removal via SSP on ECG, EOG channels
    """
    raw = ssp_ecg(raw, ssp_params_dict, n_jobs, proj_fname, proj_save_loc, ssp_topo_pattern, plot_save_loc)
    try:
        raw = ssp_eog(raw, ssp_params_dict, n_jobs, proj_fname, proj_save_loc, ssp_topo_pattern, plot_save_loc)
    except:
        logging.error('No EOG channels found')
    return raw


def ssp_eog(raw, ssp_params_dict, n_jobs, proj_fname, proj_save_loc, ssp_topo_pattern, plot_save_loc):
    # remove eye blinks via SSP, save projections and figure
    blink_projs, blinks = mne.preprocessing.ssp.compute_proj_eog(raw, **ssp_params_dict, n_jobs=n_jobs)
    if blink_projs:
        raw.add_proj(blink_projs)
        save_proj(blink_projs, proj_save_loc, proj_fname, 'EOG')
        make_topomap(raw, blink_projs, plot_save_loc, ssp_topo_pattern, 'EOG')
    log_projs(blink_projs, 'EOG')
    return raw

def ssp_ecg(raw, ssp_params_dict, n_jobs, proj_fname, proj_save_loc, ssp_topo_pattern, plot_save_loc):
    # remove heartbeats via SSP, save projections and figure
    qrs_projs, qrs = mne.preprocessing.ssp.compute_proj_ecg(raw, **ssp_params_dict, n_jobs=n_jobs)
    if qrs_projs:
        raw.add_proj(qrs_projs)
        save_proj(qrs_projs, proj_save_loc, proj_fname, 'ECG')
        make_topomap(raw, qrs_projs, plot_save_loc, ssp_topo_pattern, 'ECG')
    log_projs(qrs_projs, 'ECG')

    return raw

def maxwell_filter_paradigm(subject, raw_in, sss_out, coords, bads):
    # pass multiple arguments to a shell script for maxwell filtering via Elekta software
    cmd = './maxshell_wrapper.sh {} {} {} {} {} {} {} {}'.format(subject,
                                                                 raw_in, sss_out,
                                                                 coords[0], coords[1], coords[2],
                                                                 bads)
    proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, err = proc.communicate()
    return out, err

def maxwell_filter_erm(subject, date, raw_in, sss_out, bads):
    # pass multiple arguments to a shell script for maxwell filtering via Elekta software
    cmd = './erm_maxshell.sh {} {} {} {} {}'.format(subject, date,
                                                    raw_in, sss_out, bads)
    proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, err = proc.communicate()
    return out, err


def calculate_epochs(raw, events_baseline, event_ids, tmin, tmax, baseline, proj, reject):
    """
    :params tmin, tmax, baseline, proj, reject: part of epochs parameters dictionary to unpack
    """
    epochs = mne.Epochs(raw, events_baseline, event_ids, tmin=tmin, tmax=tmax, baseline=baseline,
                                      proj=proj, reject=reject)
    return epochs


def generate_epochs(raw, events_baseline, conditions_dicts, epochs_parameters_dict,
                    save_loc, epoch_pattern, proc_using_baseline):
    if not proc_using_baseline: # create epochs for all conditions...
        logging.info('Skipping baseline calculation')
        conditions_dicts.pop('baseline') # remove baseline condition key from conditions dictionary

    for condition_name, condition_info in conditions_dicts.items(): # loop through each condition
        condition_event_id = condition_info['event_id'] # event identifiers to epoch around
        epochs = calculate_epochs(raw, events_baseline, condition_event_id, **epochs_parameters_dict)
        log_epochs(epochs)
        save_epochs(epochs, condition_name, save_loc, epoch_pattern)

    return





# below is ICA infrastructure, definitely a work in progress...
"""
def initialize_ICA(raw, ch_type, reject, ica_params_dict, save_loc, subject):
    # initialize, fit, save ICA
    # *** seems like A LOT of parameters, could maybe pass less through use of defaults/keyword args
    n_components = ica_params_dict['n_components']
    fit_method = ica_params_dict['fit_method']
    random_state = ica_params_dict['random_state']
    ica = mne.preprocessing.ICA(n_components=n_components, method=fit_method, random_state=random_state)
    if ch_type == 'EEG':
        ica_picks = mne.pick_types(raw.info, meg=False, eeg=True, eog=True, ecg=True, stim=True, exclude='bads')
    elif ch_type == 'MEG':
        ica_picks = mne.pick_types(raw.info, meg=True, eeg=False, eog=True, ecg=True, stim=True)
    else:
        ica_picks = mne.pick_types(raw.info, meg=True, eeg=True, eog=True, ecg=True, stim=True, exclude='bads')
    ica.fit(raw, picks=ica_picks, reject=reject, decim=11)
    ica.exclude = []
    ica_fname = '{}_{}-ica.fif'.format(subject, ch_type)
    save_ica(ica, save_loc, ica_fname) # always save ICA model
    return ica


def ica_find_bads_eog(raw, ica, ch_type, save_loc, subject, save_ica_plot):
    id = 'EOG'
    eog_epochs = mne.preprocessing.create_eog_epochs(raw)
    eog_inds, eog_scores = ica.find_bads_eog(eog_epochs)
    if save_ica_plot and eog_inds:
        # make topography map figure
        make_topomap_ica(ica, eog_inds, ch_type, save_loc, subject, id)
        ica.exclude.extend(eog_inds)
    if save_ica_plot:
        # make scores figure
        plot_scores_ica(ica, eog_scores, ch_type, save_loc, subject, id)
    return ica


def ica_find_bads_ecg(raw, ica, ch_type, save_loc, subject, save_ica_plot):
    id = 'ECG'
    ecg_epochs = mne.preprocessing.create_ecg_epochs(raw)
    ecg_inds, ecg_scores = ica.find_bads_ecg(ecg_epochs)
    if save_ica_plot and ecg_inds:
        # make topography map figure
        make_topomap_ica(ica, ecg_inds, ch_type, save_loc, subject, id)
        ica.exclude.extend(ecg_inds)
    if save_ica_plot:
        # make scores figure
        plot_scores_ica(ica, ecg_scores, ch_type, save_loc, subject, id)
    return ica


def ica_find_bads_exg(raw, ica, ch_type, save_ica_plot, save_loc, subject):
    ica = ica_find_bads_eog(raw, ica, save_ica_plot, save_loc)
    ica = ica_find_bads_ecg(raw, ica, save_ica_plot, save_loc)
    if save_ica_plot:
        plot_sources_ica(raw, ica, ch_type, save_loc, subject)
    return
"""

