import mne
from os import listdir
from os.path import join
import visuals as vis
import io_helpers as i_o
import numpy as np
import fnmatch


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
                                               decim=3, n_jobs=n_jobs)
    power.save(join(save_loc, sensor_tfr_name.replace('tfr_kind', 'power')))
    itc.save(join(save_loc, sensor_tfr_name.replace('tfr_kind', 'itc')))


def compute_psd(evoked, freqs, n_jobs, save_loc, sensor_psd_fname):
    picks = ['eeg', 'meg'] if evoked.__contains__('eeg') else ['meg']
    for p in picks:
        psd, freqs = mne.time_frequency.psd_welch(evoked, fmin=freqs.min(), fmax=freqs.max(), picks=p, n_jobs=n_jobs)
        np.save(join(save_loc, sensor_psd_fname.replace('CH_TYPE', p)), psd)

    return


def analyze_sensor_space_and_add_to_report(subject, condition, sensor_subdir):
    sensor_space_files = listdir(sensor_subdir)

    for ssm in ['itc', 'power', 'psd']: # loop through sensor space metrics (ssm)
        matches = sorted(fnmatch.filter(listdir(sensor_subdir), f''))

    sensor_itc_matches = sorted(fnmatch.filter(listdir(sensor_subdir), f'{subject}*{condition}*{ssm}'))
    sensor_pow_matches = sorted(fnmatch.filter(listdir(sensor_subdir), ''))
    sensor_psd_matches = sorted(fnmatch.filter(listdir(sensor_subdir), ''))

    sensor_itcs = mne.time_frequency.read_tfrs()
    sensor_pows = mne.time_frequency.read_tfrs()
    sensor_psds = np.load()

    return



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

