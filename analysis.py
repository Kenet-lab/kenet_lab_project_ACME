import mne
from os.path import join
import visuals as vis
import io_helpers as i_o
import numpy as np


def calc_sensor_tfr(epochs, freqs, n_cycles, n_jobs, save_loc, sensor_tfr_name, paradigm):
    """
    :param epochs: epochs to calculate TFR objects from
    :param freqs: frequencies of interest
    :param n_jobs: job control to speed up computation
    :return: power and ITC TFR objects
    """
    if paradigm in ['fix', 'fixation', 'RestingState', 'EyesClosed', 'EyesOpen']:
        return
    power, itc = mne.time_frequency.tfr_morlet(epochs, freqs=freqs, n_cycles=n_cycles, use_fft=True, return_itc=True,
                                               decim=1, n_jobs=n_jobs)
    power.save(join(save_loc, sensor_tfr_name.replace('tfr_kind', 'power')), overwrite=True)
    itc.save(join(save_loc, sensor_tfr_name.replace('tfr_kind', 'itc')), overwrite=True)


def compute_psd(evoked, freqs, n_jobs, save_loc, sensor_psd_fname):
    picks = ['eeg', 'meg'] if evoked.__contains__('eeg') else ['meg']
    for p in picks:
        psd, freqs = mne.time_frequency.psd_welch(evoked, fmin=freqs.min(), fmax=freqs.max(), picks=p, n_jobs=n_jobs)
        np.save(join(save_loc, sensor_psd_fname.replace('CH_TYPE', p)), psd)
        np.save(join(save_loc, sensor_psd_fname.replace('CH_TYPE', f'{p}_freqs')), freqs)
    return


def analyze_sensor_space_and_make_figures(sensor_subdir, sensor_tfr_name, sensor_psd_name, freqs, tfr_temporal_dict,
                                          sensor_tfr_plot_name, sensor_psd_plot_name):
    # LOAD/IMPORT DATA
    itc_match = i_o.find_file_matches(sensor_subdir, f"{sensor_tfr_name.replace('tfr_kind', 'itc')}")
    power_match = i_o.find_file_matches(sensor_subdir, f"{sensor_tfr_name.replace('tfr_kind', 'power')}")
    psd_matches = sorted(i_o.find_file_matches(sensor_subdir, f"{sensor_psd_name.replace('CH_TYPE', '???')}"))
    psd_freq_matches = sorted(i_o.find_file_matches(sensor_subdir, f"{sensor_psd_name.replace('CH_TYPE', '???_freqs')}"))
    try:
        itc = mne.time_frequency.read_tfrs(join(sensor_subdir, itc_match[0]))[0]
        power = mne.time_frequency.read_tfrs(join(sensor_subdir, power_match[0]))[0]
    except IndexError: # no ITC/power TFR data available, because paradigm is fixation
        itc = None
        power = None

    psds = [np.load(join(sensor_subdir, psd_match)) for psd_match in psd_matches]
    psds_freqs = [np.load(join(sensor_subdir, psd_freq_match)) for psd_freq_match in psd_freq_matches]
    psd_eeg = psds[0] if len(psds) == 2 else None
    psd_meg = psds[-1]

    # DETERMINE EEG AVAILABILITY
    picks = ['eeg', 'meg'] if isinstance(psd_eeg, np.ndarray) else ['meg']

    t_start = tfr_temporal_dict['t_start']
    t_end = tfr_temporal_dict['t_end']

    # check if ITC/power are available (not None), then begin analyzing
    if not isinstance(itc, type(None)):
        # ITC and power available...
        vis.plot_sensor_space_tfr(itc, power, picks, sensor_subdir, sensor_tfr_plot_name.replace('filler', 'TFR'))

        itc_cropped = itc.copy().crop(tmin=t_start, tmax=t_end)
        # make ITC channels figure
        vis.plot_sensor_channels_arrays_by_frequency(itc_cropped, None, picks, sensor_subdir,
                                                     sensor_tfr_plot_name.replace('filler', f'{int(t_start*1000)}_{int(t_end*1000)}_ITC'))
    # make PSD channels figure
    vis.plot_sensor_channels_arrays_by_frequency(psds, psds_freqs, picks, sensor_subdir, sensor_psd_plot_name)



def analyze_sensor_tfr(tfr, tfr_temporal_dict, save_loc, plot_fname):
    """
    :param tfr: TFR object to manipulate
    :param tfr_temporal_dict: dictionary containing parameters on what/how to manipulate TFR
    """
    t_start = tfr_temporal_dict['t_start']
    t_end = tfr_temporal_dict['t_end']
    tfr_crop = tfr.crop(tmin=t_start, tmax=t_end) # manipulation could be improved (ex: frequency cropping)
    tfr_kind = tfr.method.split('-')[1] # infer if the TFR object is power or ITC...

    picks = ['eeg', 'meg'] if tfr.__contains__('eeg') else ['meg']
    for p in picks:
        tfr_picked = tfr_crop.copy().pick(picks=p) # pick/index EEG or MEG or both
        plot_fname_picked = i_o.format_variable_names({'filler': f'{int(t_start*1000)}_{int(t_end*1000)}_{p}',
                                                       'tfr_kind': tfr_kind}, plot_fname)
        # plotting could use improvement
        vis.plot_sensor_tfr_aggregate(tfr_picked, save_loc, plot_fname_picked)
        vis.plot_sensor_tfr_channels(tfr_picked.data.mean(axis=2), tfr_picked.freqs, save_loc, plot_fname_picked)
    return

