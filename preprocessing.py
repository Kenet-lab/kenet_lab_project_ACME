import mne
import logging
import numpy as np
import io_mod as i_o
import visuals as vis
from os.path import join


def apply_bad_channels_eeg(raw, loc, eeg_bads_fname): # read, and add bad EEG channels to raw data
    """
    :param raw: raw file to add marked bad EEG channels to
    :param loc: string of location to read bad channels .txt from
    :param eeg_bads_fname: string of subject+paradigm specific bad EEG channels filename
    :return: raw fif with bad EEG channels added to header
    """
    eeg_bads = i_o.read_bad_channels_eeg(loc, eeg_bads_fname) # read the bad channels .txt file
    logging.info(f'Adding the following bad EEG channels to {i_o.get_subject_id_from_data(raw)}:\n{eeg_bads}')
    raw.info['bads'].extend(eeg_bads) # add the bad channels to the raw file
    return raw


def apply_notch_filter(raw, n_jobs, loc, eeg_bads_fname):
    """
    :param raw: raw file to notch filter
    :param n_jobs: job control for speeding up computation
    :param loc: string of location to read bad EEG channels from, required to do so before notch filtering
    :param eeg_bads_fname: string of subject+paradigm specific bad EEG channels filename
    :return: notch filtered raw fif file
    """
    linefreq = raw.info['line_freq'] # notch filter line frequency
    raw = apply_bad_channels_eeg(raw, loc, eeg_bads_fname) # add bad EEG channels
    for harmonic_num in [1, 2, 3]: # notch filter its second and third harmonics
        notch_freq = linefreq * harmonic_num
        raw.notch_filter(np.arange(notch_freq, 241, notch_freq), picks=['eeg'], n_jobs=n_jobs)
    return raw


def filter_signal(raw, l_freq, h_freq, n_jobs, eeg, save_loc_eeg, eeg_bads_fname, save_loc_signal, signal_fname):
    """
    :param raw: signal to bandpass filter
    :param l_freq: lower cutoff frequency
    :param h_freq: higher cutoff frequency
    :param n_jobs: job control for speeding up computation
    :param eeg: bool stating whether EEG is to be processed
    :param save_loc_eeg: string of location where bad EEG channels .txt can be found
    :param eeg_bads_fname: string of subject+paradigm specific filename for bad EEG channels .txt
    :param save_loc_signal: string of location in which we save the bandpass filtered signal
    :param signal_fname: string of filename for the bandpass filtered signal
    :return: bandpass filtered signal
    """
    raw.load_data()
    raw = apply_notch_filter(raw, n_jobs, save_loc_eeg, eeg_bads_fname) if eeg and raw.__contains__('eeg') else raw
    raw.filter(l_freq=l_freq, h_freq=h_freq, n_jobs=n_jobs) # filter the signal accordingly
    raw.save(join(save_loc_signal, signal_fname))
    return raw


def generate_head_origin(info, subject_meg_dir, head_origin_fname): # calculate, save head origin coordinates
    """
    :param info: MNE Info object
    :param subject_meg_dir: string of location to save the head origin coordinates
    :param head_origin_fname: string of filename to save the head origin coordinates
    :return: head origin coordinates array -> [x y z] in METERS!
    """
    all_coords = mne.bem.fit_sphere_to_headshape(info, units='m') # calculate head origin coordinates
    head_origin = all_coords[1]
    logging.info('Head origin coordinates are:\n{}'.format(head_origin))
    np.savetxt(join(subject_meg_dir, head_origin_fname), head_origin) # save the coordinates
    return head_origin


def ssp_exg(raw, ssp_params_dict, n_jobs, proj_fname, proj_save_loc, ssp_topo_pattern, plot_save_loc):
    """
    :param raw: raw file to remove artifacts from
    :param ssp_params_dict: dictionary containing relevant SSP parameters
    :param n_jobs: job control for speeding up computation
    :param proj_fname: string of filename to save projections
    :param ssp_topo_pattern: string of filename to save plot topographies of projections
    :return: signal with ExG projections applied
    perform artifact detection and removal via SSP on ECG, EOG channels
    """
    raw = ssp_ecg(raw, ssp_params_dict, n_jobs, proj_fname, proj_save_loc, ssp_topo_pattern, plot_save_loc)
    try: # try to remove ocular artifacts, can fail if no EOG channels are found
        raw = ssp_eog(raw, ssp_params_dict, n_jobs, proj_fname, proj_save_loc, ssp_topo_pattern, plot_save_loc)
    except IndexError:
        logging.error('No EOG channels found') # build handling of the scenario where EOG channels are not found
        # or: EOG channels were marked as bad
    return raw


def ssp_eog(raw, ssp_params_dict, n_jobs, proj_fname, proj_save_loc, ssp_topo_pattern, plot_save_loc):
    # remove eye blinks via SSP, save projections and figure
    blink_projs, blinks = mne.preprocessing.ssp.compute_proj_eog(raw, **ssp_params_dict, n_jobs=n_jobs)
    if blink_projs:
        raw.add_proj(blink_projs)
        i_o.save_proj(blink_projs, proj_save_loc, proj_fname, 'EOG')
        vis.make_topomap(raw, blink_projs, plot_save_loc, ssp_topo_pattern, 'EOG')
    i_o.log_projs(blink_projs, 'EOG')
    return raw


def ssp_ecg(raw, ssp_params_dict, n_jobs, proj_fname, proj_save_loc, ssp_topo_pattern, plot_save_loc):
    # remove heartbeats via SSP, save projections and figure
    qrs_projs, qrs = mne.preprocessing.ssp.compute_proj_ecg(raw, **ssp_params_dict, n_jobs=n_jobs)
    if qrs_projs:
        raw.add_proj(qrs_projs)
        i_o.save_proj(qrs_projs, proj_save_loc, proj_fname, 'ECG')
        vis.make_topomap(raw, qrs_projs, plot_save_loc, ssp_topo_pattern, 'ECG')
    i_o.log_projs(qrs_projs, 'ECG')
    return raw


def generate_epochs(raw, events_baseline, conditions_dicts, epochs_parameters_dict,
                    save_loc, epoch_pattern, proc_using_baseline):
    """
    :param raw: raw file to create epochs from
    :param conditions_dicts: dictionary of dictionaries detailing various conditon names, and their event IDs
    :param epochs_parameters_dict: dictionary of epoching parameters
    :param proc_using_baseline: bool stating to either use a noise covariance from baseline or ERM
    """
    if not proc_using_baseline: # create epochs for all conditions...
        logging.info('Skipping baseline calculation...')
        conditions_dicts.pop('baseline') # remove baseline condition key from conditions dictionary

    for condition_name, condition_info in conditions_dicts.items(): # loop through each condition
        condition_event_id = condition_info['event_id'] # event identifiers to epoch around
        epochs_parameters_dict.update({'event_id': condition_event_id})
        epochs = mne.Epochs(raw, events_baseline, **epochs_parameters_dict) # calculate the epochs
        i_o.log_epochs(epochs)
        i_o.save_epochs(epochs, condition_name, save_loc, epoch_pattern) # save the epochs accordingly
    return epochs


def calc_head_position(raw, save_loc, fname):
    """
    calculate head position matrix for movement compensation during SSS/maxwell filtering
    :param raw: raw file to generate head position matrix for
    :return: head postion array
    """
    ext_order = 3
    chpi_amplitudes = mne.chpi.compute_chpi_amplitudes(raw, ext_order=ext_order)
    chpi_locs = mne.chpi.compute_chpi_locs(raw.info, chpi_amplitudes)
    head_pos = mne.chpi.compute_head_pos(raw.info, chpi_locs)
    np.savetxt(join(save_loc, fname), head_pos)
    return head_pos


def find_bads_meg(raw, sss_params, subject_preproc_dir, meg_bads_fname, n_jobs):
    """
    automatic bad MEG channel detection
    :param raw: raw file to find bad MEG channels
    :param sss_params: dictionary containing relevant SSS/maxwell filtering parameters
    :return: raw file with bad MEG channels added to its header, as well as the bad channels detected
    """
    lp = 40.
    raw_copy = raw.copy().load_data().filter(None, lp, n_jobs=n_jobs) # recommended to filter below 40 Hz prior to detection
    for key in ['st_correlation', 'destination', 'st_duration']:
        sss_params.pop(key) # remove un-needed arguments from parameters dictionary
    noisy, flat = mne.preprocessing.find_bad_channels_maxwell(raw_copy, **sss_params) # find the bad channels
    del raw_copy
    bads = noisy + flat
    np.savetxt(join(subject_preproc_dir, meg_bads_fname), bads) # save the bad channels
    raw.info['bads'].extend(bads) # add the bad channels to the raw fif
    return raw, bads


def mne_maxwell_filter_paradigm(raw, sss_params, subject_preproc_dir, subject_sss_fname):
    """
    perform SSS on a non-ERM signal
    :param sss_params: dictionary containing relevant SSS/maxwell filtering parameters
    :return: SSS'd signal
    """
    sss = mne.preprocessing.maxwell_filter(raw, **sss_params)
    sss.save(join(subject_preproc_dir, subject_sss_fname)) # save the SSS'd file
    return sss


def mne_maxwell_filter_erm(raw_erm, bads, sss_params, subject_preproc_dir, subject_erm_sss_fname):
    """
    perform SSS on ERM data - used for noise covariance matrices later during MRI processing
    :param raw: raw ERM file
    :param sss_params: dictionary containing relevant SSS/maxwell filtering parameters
    :return: SSS'd ERM file
    """
    # remove parameters from sss params dictionary for ERM processing
    for key in ['destination', 'head_pos']: # ERM processing does not need a head transformation matrix
        sss_params[key] = None # no need to perform movement compensation
    sss_params['coord_frame'] = 'meg'
    sss_params['origin'] = 'auto'
    raw_erm.info['bads'].extend(bads) # add bad channels to ERM fif header
    erm_sss = mne.preprocessing.maxwell_filter(raw_erm, **sss_params)
    erm_sss.save(join(subject_preproc_dir, subject_erm_sss_fname))
    return erm_sss










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
    
outdated maxwell filtering code...
def maxwell_filter_paradigm(subject, raw_in, sss_out, coords, bads):
    # pass multiple arguments to a shell script for maxwell filtering via Elekta software
    cmd = './maxshell_wrapper.sh {} {} {} {} {} {} {} {}'.format(subject,
                                                                 raw_in, sss_out,
                                                                 coords[0], coords[1], coords[2],
                                                                 bads)
    logging.info('Adding the following bad channels (MEG) to {}:\n{}'.format(subject, bads))
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
"""

