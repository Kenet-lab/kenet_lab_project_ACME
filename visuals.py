import mne
import matplotlib.pyplot as plt
from os.path import join, isfile
import io_helpers as i_o
from mayavi import mlab


def make_topomap(raw, projs, save_loc, ssp_topo_pattern, kind):
    """ plot topographies of SSP projections
    :param raw: raw data
    :param projs: projections to plot
    :param kind: string denoting whether the projections are EOG, ECG..."""
    fig_topo_fname = i_o.format_variable_names({'kind': kind}, ssp_topo_pattern)
    fig_topo = mne.viz.plot_projs_topomap(projs, raw.info, show=False) # plot, save topographies of SSP projections
    fig_topo.savefig(join(save_loc, fig_topo_fname))
    return


def plot_evoked_sensor(epochs, save_loc, evoked_sensor_pattern):
    evoked = epochs.average()
    fig_list = evoked.plot_joint(show=False, exclude='bads')
    for i, fig in enumerate(fig_list):
        fig_evoked_sensor_fname = i_o.format_variable_names({'filler': i}, evoked_sensor_pattern)
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
    plt.title(ch_plot_fname.replace('.png', ''), fontsize=12)
    plt.savefig(join(save_loc, ch_plot_fname))
    plt.close()
    return


def make_report_sensor_space(subject, condition_name, fig_save_loc, fig_save_name,
                             report_save_loc, report_save_name, tfr_temporal_dict):

    report_path = join(report_save_loc, report_save_name) # full path to report's location
    sensor_report = mne.open_report(report_path) if isfile(report_path) else mne.Report() # create or load report
    # load corresponding condition, and time window
    t_start = int(tfr_temporal_dict['t_start']) * 1000
    t_end = int(tfr_temporal_dict['t_end']) * 1000
    # load the image(s)
    img_pattern = i_o.format_variable_names({'filler': f'{t_start}_{t_end}_*', 'tfr_kind': 'itc'}, fig_save_name)
    img_matches = i_o.find_file_matches(fig_save_loc, img_pattern)
    for img in img_matches:
        sensor_report.add_images_to_section(join(fig_save_loc, img), captions=subject, section=condition_name, scale=3)
    sensor_report.save(join(report_save_loc, report_save_name), open_browser=True, overwrite=True)
    return


def plot_coreg_alignment(info, trans, subject, subjects_dir, save_loc, save_name):
    fig_alignment = mne.viz.plot_alignment(info, trans, subject=subject,
                                           dig=True, meg=['helmet', 'sensors'],
                                           subjects_dir=subjects_dir, surfaces='brain')
    fig_alignment.scene.save(join(save_loc, save_name))
    mlab.close()
    return


def plot_bem(subject, subjects_dir, save_loc, save_name):
    fig_bem = mne.viz.plot_bem(subject=subject, subjects_dir=subjects_dir,
                               brain_surfaces='white', orientation='coronal', show=True)
    fig_bem.savefig(join(save_loc, save_name))
    plt.close(fig_bem)
    return
