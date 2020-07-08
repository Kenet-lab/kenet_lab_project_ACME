import mne
from os.path import join
import visuals as vis
import io_helpers as i_o


def calc_sensor_tfr(epochs, freqs, n_cycles, n_jobs, save_loc, sensor_tfr_name):
    """
    :param epochs: epochs to calculate TFR objects from
    :param freqs: frequencies of interest
    :param n_jobs: job control to speed up computation
    :return: power and ITC TFR objects
    """
    power, itc = mne.time_frequency.tfr_morlet(epochs, freqs=freqs, n_cycles=n_cycles, use_fft=True,
                                               return_itc=True, decim=3, n_jobs=n_jobs)
    power.save(join(save_loc, sensor_tfr_name.replace('tfr_kind', 'power')))
    itc.save(join(save_loc, sensor_tfr_name.replace('tfr_kind', 'itc')))
    return power, itc


def analyze_sensor_tfr(tfr, tfr_temporal_dict, save_loc, plot_fname, eeg):
    """
    :param tfr: TFR object to manipulate
    :param tfr_temporal_dict: dictionary containing parameters on what/how to manipulate TFR
    """
    # tfr_temporal_dict['sliding'] = True/False... turn sliding window computations on/off
    if not tfr_temporal_dict['sliding']:
        t_start = tfr_temporal_dict['t_start']
        t_end = tfr_temporal_dict['t_end']
        tfr_crop = tfr.crop(tmin=t_start, tmax=t_end) # manipulation could be improved (ex: frequency cropping)
        tfr_kind = tfr.method.split('-')[1] # infer if the TFR object is power or ITC...
        # check if EEG available
        picks = ['eeg', 'meg', ['meg', 'eeg']] if eeg and tfr.__contains__('eeg') else ['meg']
        for p in picks:
            tfr_picked = tfr_crop.copy().pick(picks=p) # pick/index EEG or MEG or both
            plot_fname_picked = i_o.format_variable_names({'filler': f'{int(t_start*1000)}_{int(t_end*1000)}_{p}',
                                                           'tfr_kind': tfr_kind}, plot_fname)
            # plotting could use improvement
            vis.plot_sensor_tfr_aggregate(tfr_picked, save_loc, plot_fname_picked)
            vis.plot_sensor_tfr_channels(tfr_picked.data.mean(axis=2), tfr_picked.freqs, save_loc, plot_fname_picked)
    return
