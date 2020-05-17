import mne
import logging
from os.path import join
from visuals import *
from preprocessing import *
from io_mod import *


def calc_evoked(epochs):
    try: # this will fail if EEG electrode locations overlap... implement a solution
        evoked = epochs.average()
        return evoked
    except:
        logging.error('Problem calculating evoked response...\n')
        return


def calc_sensor_tfr(epochs, freqs, n_cycles, n_jobs, save_loc, sensor_tfr_name):
    power, itc = mne.time_frequency.tfr_morlet(epochs, freqs=freqs, n_cycles=n_cycles, use_fft=True,
                                               return_itc=True, decim=3, n_jobs=n_jobs)
    power.save(join(save_loc, sensor_tfr_name.replace('kind', 'power')))
    itc.save(join(save_loc, sensor_tfr_name.replace('kind', 'itc')))
    return power, itc


def manipulate_sensor_tfr(tfr, tfr_temporal_dict, save_loc, agg_plot_fname, ch_plot_fname, eeg):
    """
    this function will interface with functions handling plotting, saving of plots as well
    """
    # tfr_temporal_dict['sliding'] = True/False... turn sliding window computations on/off
    if not tfr_temporal_dict['sliding']:
        t_start = tfr_temporal_dict['t_start']
        t_end = tfr_temporal_dict['t_end']
        tfr_crop = tfr.crop(tmin=t_start, tmax=t_end)
        # check if EEG available
        picks = ['eeg', 'meg', ['meg', 'eeg']] if eeg and check_eeg_availability(tfr) else ['meg']
        for p in picks:
            tfr_picked = tfr_crop.pick(picks=p)

            replace_dict = {'channel_type': p}
            agg_plot_fname, ch_plot_fname = format_variable_names(replace_dict, agg_plot_fname, ch_plot_fname)

            plot_sensor_tfr_aggregate(tfr_picked, save_loc, agg_plot_fname)
            plot_sensor_tfr_channels(tfr_picked.data.mean(axis=2), tfr_picked.freqs, save_loc, ch_plot_fname)
    return
