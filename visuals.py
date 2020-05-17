import mne
import matplotlib.pyplot as plt
import logging
from os.path import join
from analysis import *
from io_mod import *
from preprocessing import *


def make_topomap(raw, projs, save_loc, ssp_topo_pattern, kind):
    replace_dict = {'subject': get_subject_id_from_data(raw), 'kind': kind}
    fig_topo_fname = format_variable_names(replace_dict, ssp_topo_pattern)

    fig_topo = mne.viz.plot_projs_topomap(projs, raw.info, show=False) # plot, save topographies of SSP projections
    fig_topo.savefig(join(save_loc, fig_topo_fname))
    return


def plot_evoked_sensor(epochs, save_loc, evoked_sensor_pattern):
    evoked = calc_evoked(epochs)
    fig_list = evoked.plot_joint(show=False, exclude='bads')
    for i, fig in enumerate(fig_list):
        replace_dict = {'subject': get_subject_id_from_data(epochs), 'fignum': i}
        fig_evoked_sensor_fname = format_variable_names(replace_dict, evoked_sensor_pattern)
        fig.savefig(join(save_loc, fig_evoked_sensor_fname))
    return


def plot_sensor_tfr_aggregate(tfr, save_loc, agg_plot_fname):
    fig = tfr.plot(show=False, combine='mean')
    fig.savefig(join(save_loc, agg_plot_fname))
    return

def plot_sensor_tfr_channels(sensor_array, freqs, save_loc, ch_plot_fname):
    plt.figure(1, clear=True)
    plt.plot(freqs, sensor_array.T)
    plt.ylim((0, 0.75))
    plt.xlabel('Frequency [Hz]', fontsize=12)
    plt.ylabel('Intertrial Coherence', fontsize=12)
    plt.title(ch_plot_fname.replace('_channels_sensor_itc.png', ''), fontsize=12)
    plt.savefig(join(save_loc, ch_plot_fname))
    plt.close()
    return












# similar to preprocessing.py, functions below are ICA infrastructure (WIP)
"""
def make_topomap_ica(ica, exg_inds, ch_type, save_loc, subject, id):
    fig_topo = ica.plot_components(exg_inds, show=False)
    fig_name = '{}_{}_{}_ica-topo.png'.format(subject, ch_type, id)
    fig_topo.savefig(join(save_loc, fig_name))
    return


def plot_scores_ica(ica, scores, ch_type, save_loc, subject, id):
    fig_scores = ica.plot_scores(scores, show=False)
    fig_name = '{}_{}_{}_ica-scores.png'.format(subject, ch_type, id)
    fig_scores.savefig(join(save_loc, fig_name))
    return


def plot_sources_ica(raw, ica, ch_type, save_loc, subject):
    fig_sources = ica.plot_sources(raw, show=False)
    fig_name = '{}_{}_components_timeseries.png'.format(subject, ch_type)
    fig_sources.savefig(join(save_loc, fig_name))
    return
"""

