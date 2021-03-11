import mne
import logging
import autoreject
import numpy as np
import io_helpers as i_o
import visuals as vis
from os.path import join


def apply_notch_filter_to_eeg(raw, n_jobs, loc, eeg_bads_fname, epochs_parameters_dict):
    """
    :param raw: raw file to notch filter
    :param n_jobs: job control for speeding up computation
    :param loc: string of location to read bad EEG channels from, required to do so before notch filtering
    :param eeg_bads_fname: string of subject+paradigm specific bad EEG channels filename
    :return: notch filtered raw fif file
    """
    linefreq = raw.info['line_freq'] # notch filter line frequency
    raw = find_bads_eeg(raw, epochs_parameters_dict, n_jobs, loc, eeg_bads_fname) # find and add bad EEG channels
    for harmonic_num in [1, 2]: # notch filter its second harmonic, too
        notch_freq = linefreq * harmonic_num
        raw.notch_filter(np.arange(notch_freq, 241, notch_freq), picks=['eeg'], n_jobs=n_jobs)
    return raw

def filter_signal(raw, l_freq, h_freq, n_jobs, save_loc, signal_fname, eeg_bads_fname, epochs_parameters_dict, save=True):
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
    raw.filter(l_freq=l_freq, h_freq=h_freq, n_jobs=n_jobs) # filter the signal accordingly
    if raw.__contains__('eeg'):
        raw.set_montage('mgh70') # import correct cap layout
        raw.set_eeg_reference(ref_channels='average') # apply average reference
        raw = apply_notch_filter_to_eeg(raw, n_jobs, save_loc, eeg_bads_fname, epochs_parameters_dict)
    if save:
        raw.save(join(save_loc, signal_fname), overwrite=True)
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


def ssp_exg(raw, ssp_dict, n_jobs, proj_fname, proj_save_loc, ssp_topo_pattern, plot_save_loc):
    """
    :param raw: raw file to remove artifacts from
    :param ssp_dict: dictionary whose keys: 'params' parameters dictionary,
    :param n_jobs: job control for speeding up computation
    :param proj_fname: string of filename to save projections
    :param ssp_topo_pattern: string of filename to save plot topographies of projections
    :return: signal with ExG projections applied
    perform artifact detection and removal via SSP on ECG, EOG channels
    """
    ecg_fab_channels_all = ssp_dict['ecg_fab_channels']
    eog_fab_channels_all = ssp_dict['eog_fab_channels']
    # make sure fabrication channels are not bad channels
    ecg_fab_channels_usable = [ecg_fch for ecg_fch in ecg_fab_channels_all if ecg_fch not in raw.info['bads']]
    eog_fab_channels_usable = [eog_fch for eog_fch in eog_fab_channels_all if eog_fch not in raw.info['bads']]

    qrs_projs = ssp_ecg(raw, ssp_dict['params'], ecg_fab_channels_usable, n_jobs, proj_fname, proj_save_loc,
                        ssp_topo_pattern, plot_save_loc)
    blink_projs = ssp_eog(raw, ssp_dict['params'], eog_fab_channels_usable, n_jobs, proj_fname, proj_save_loc,
                          ssp_topo_pattern, plot_save_loc)
    for proj in [qrs_projs, blink_projs]:
        if proj:
            raw.add_proj(proj)
    raw.apply_proj() # clean the data
    return raw

def ssp_ecg(raw, ssp_params, ecg_fab_channels, n_jobs, proj_fname, proj_save_loc, ssp_topo_pattern, plot_save_loc):
    # detect heartbeats via SSP, save projections and topography figure
    if not raw.__contains__('ecg'): # use MEG channels to detect heartbeats
        qrs_projs = find_ecg_artifacts_without_ecg_channel(raw, ssp_params, ecg_fab_channels, n_jobs)
    else:
        qrs_projs, qrs = mne.preprocessing.ssp.compute_proj_ecg(raw, **ssp_params, n_jobs=n_jobs)
    if qrs_projs:
        i_o.save_proj(qrs_projs, proj_save_loc, proj_fname, 'ECG')
        vis.make_topomap(raw, qrs_projs, plot_save_loc, ssp_topo_pattern, 'ECG')
        i_o.log_projs(qrs_projs, 'ECG')
    return qrs_projs

def find_ecg_artifacts_without_ecg_channel(raw, ssp_params, ecg_fab_channels, n_jobs):
    for channel in ecg_fab_channels:
        qrs_projs, qrs = mne.preprocessing.ssp.compute_proj_ecg(raw, **ssp_params, n_jobs=n_jobs, ch_name=channel)
        if qrs_projs:
            break
    return qrs_projs

def ssp_eog(raw, ssp_params, eog_fab_channels, n_jobs, proj_fname, proj_save_loc, ssp_topo_pattern, plot_save_loc):
    # detect eye blinks via SSP, save projections and topography figure
    if not raw.__contains__('eog'): # use EEG or MEG channels to detect eye blinks
        blink_projs = find_eog_artifacts_without_eog_channel(raw, ssp_params, eog_fab_channels, n_jobs)
    else:
        blink_projs, blinks = mne.preprocessing.ssp.compute_proj_eog(raw, **ssp_params, n_jobs=n_jobs)
    if blink_projs:
        i_o.save_proj(blink_projs, proj_save_loc, proj_fname, 'EOG')
        vis.make_topomap(raw, blink_projs, plot_save_loc, ssp_topo_pattern, 'EOG')
        i_o.log_projs(blink_projs, 'EOG') # add a message argument (ex: frontal channels were used)
    return blink_projs

def find_eog_artifacts_without_eog_channel(raw, ssp_params, eog_fab_channels, n_jobs):
    if raw.__contains__('eeg'):
        eog_fab_channels_available = eog_fab_channels
    else:
        eog_fab_channels_available = [eog_fch_avail for eog_fch_avail in eog_fab_channels if 'EEG' not in eog_fch_avail]

    for channel in eog_fab_channels_available:
        blink_projs, blinks = mne.preprocessing.ssp.compute_proj_eog(raw, **ssp_params, n_jobs=n_jobs, ch_name=channel)
        if blink_projs:
            break
    return blink_projs


def generate_epochs(raw, events, conditions_dicts, epochs_parameters_dict,
                    save_loc, epoch_pattern):
    """
    :param raw: raw file to create epochs from
    :param events: numpy array containing events over time
    :param conditions_dicts: dictionary of dictionaries detailing various conditon names, and their event IDs
    :param epochs_parameters_dict: dictionary of epoching parameters
    """
    if not raw.__contains__('eeg'):
        del epochs_parameters_dict['reject']['eeg']
    for condition_name, condition_info in conditions_dicts.items(): # loop through each condition
        condition_event_id = condition_info['event_id'] # event identifiers to epoch around
        epochs_parameters_dict.update({'event_id': condition_event_id})
        epochs = mne.Epochs(raw, events, **epochs_parameters_dict) # calculate the epochs
        i_o.log_epochs(epochs)
        i_o.save_epochs(epochs, condition_name, save_loc, epoch_pattern) # save the epochs accordingly


def calc_head_position(raw, save_loc, fname):
    """
    calculate head position matrix for movement compensation during SSS/maxwell filtering
    :param raw: raw file to generate head position matrix for
    :return: head postion array
    """
    if not raw.__contains__('chpi'):
        head_pos = None
    else:
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
    for key in ['st_correlation', 'destination', 'st_duration']:
        sss_params.pop(key) # remove un-needed arguments from parameters dictionary
    noisy, flat = mne.preprocessing.find_bad_channels_maxwell(raw, **sss_params) # find the bad channels
    bads = noisy + flat
    i_o.save_bad_channels(raw, bads, subject_preproc_dir, meg_bads_fname) # save accordingly
    return bads


def find_bads_eeg(raw, epochs_parameters_dict, n_jobs, subject_preproc_dir, eeg_bads_fname):

    events = mne.find_events(raw, stim_channel='STI101', shortest_event=1)
    eeg_data = raw.copy().pick_types(meg=False, eeg=True)

    eeg_epochs = mne.Epochs(eeg_data, events, tmin=epochs_parameters_dict['tmin'], tmax=epochs_parameters_dict['tmax'],
                            baseline=epochs_parameters_dict['baseline'], proj=False, reject=None, preload=True)

    picks = mne.pick_types(eeg_epochs.info, meg=False, eeg=True)

    ransac = autoreject.Ransac(unbroken_time=0.3, picks=picks, n_jobs=n_jobs)
    ransac.fit(eeg_epochs)

    bads = ransac.bad_chs_
    raw.info['bads'].extend(bads)
    i_o.save_bad_channels(raw, bads, subject_preproc_dir, eeg_bads_fname) # save accordingly
    return raw


def mne_maxwell_filter_paradigm(raw, sss_params, subject_preproc_dir, subject_sss_fname, save):
    """
    perform SSS on a non-ERM signal
    :param sss_params: dictionary containing relevant SSS/maxwell filtering parameters
    :param save: boolean for saving the SSS'd signal
    :return: SSS'd signal
    """
    sss = mne.preprocessing.maxwell_filter(raw, **sss_params)
    if save:
        sss.save(join(subject_preproc_dir, subject_sss_fname)) # save the SSS'd file
    return sss


def mne_maxwell_filter_erm(raw_erm, bads_list, sss_params, subject_preproc_dir, subject_erm_sss_fname, save=True):
    """
    perform SSS on ERM data - used for noise covariance matrices later during MRI processing
    :param raw: raw ERM file
    :param bads_list: list of lists of strings containing automatically detected bad MEG channels
    :param sss_params: dictionary containing relevant SSS/maxwell filtering parameters
    :return: SSS'd ERM file
    """
    # remove parameters from sss params dictionary for ERM processing
    for key in ['destination', 'head_pos']: # ERM processing does not need a head transformation matrix
        sss_params[key] = None # no need to perform movement compensation
    sss_params['coord_frame'] = 'meg'
    sss_params['origin'] = 'auto'

    bads_list_flattened = [bad_ch for bads_sublist in bads_list for bad_ch in bads_sublist] # flatten the list of lists
    bads_unique = list(set(bads_list_flattened)) # remove duplicate channels that were auto-detected

    raw_erm.info['bads'].extend(bads_unique) # add bad channels to ERM fif header
    erm_sss = mne.preprocessing.maxwell_filter(raw_erm, **sss_params)
    if save:
        erm_sss.save(join(subject_preproc_dir, subject_erm_sss_fname))
    return erm_sss
