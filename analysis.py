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


def calc_sensor_itc(epochs, freqs, n_cycles, n_jobs, save_loc, sensor_itc_fname): # inter-trial coherence
    power, itc = mne.time_frequency.tfr_morlet(epochs, freqs=freqs, n_cycles=n_cycles,
                                               use_fft=True, return_itc=True, decim=3,
                                               n_jobs=n_jobs)
    save_sensor_itc(itc, save_loc, sensor_itc_fname)
    return itc


def manipulate_sensor_itc(itc, itc_params_dict, save_loc, agg_plot_fname, ch_plot_fname, eeg):
    """
    this function will interface with functions handling plotting, saving of plots as well
    """
    # itc_params_dict['sliding'] = True/False... turn sliding window computations on/off
    if not itc_params_dict['sliding']: # perform non-sliding computations
        t_start = itc_params_dict['t_start']
        t_end = itc_params_dict['t_end']
        itc_crop = itc.crop(tmin=t_start, tmax=t_end)
        # check if EEG available
        picks = ['eeg', 'meg', ['meg', 'eeg']] if eeg and check_eeg_availability(itc) else ['meg']
        for p in picks:
            itc_picked = itc_crop.pick(picks=p)

            replace_dict = {'channel_type': p}
            agg_plot_fname, ch_plot_fname = format_variable_names(replace_dict, agg_plot_fname, ch_plot_fname)

            plot_sensor_itc_aggregate(itc_picked, save_loc, agg_plot_fname)
            plot_sensor_itc_channels(itc_picked.data.mean(axis=2), itc_picked.freqs, save_loc, ch_plot_fname)
