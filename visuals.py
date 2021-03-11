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


def plot_sensor_space_tfr(itc, power, picks, save_loc, save_name):
    fig, axs = plt.subplots(2, len(picks), sharex=True, sharey=True)
    for idx, pick in enumerate(picks):
        itc_ax = axs[0, idx] if len(picks) == 2 else axs[0]
        pow_ax = axs[1, idx] if len(picks) == 2 else axs[1]
        itc.plot(picks=pick, baseline=None, show=False, combine='mean', axes=itc_ax, exclude='bads', colorbar=False)
        power.plot(picks=pick, baseline=None, show=False, combine='mean', axes=pow_ax, exclude='bads', colorbar=False)
        axs[0, idx].set_title(f'ITC: {pick.upper()}')
        axs[1, idx].set_title(f'Power: {pick.upper()}')
    fig.suptitle('Sensor space time-frequency')
    fig.savefig(join(save_loc, save_name))
    plt.close(fig)


def plot_sensor_channels_arrays_by_frequency(sensor_data, freqs, picks, save_loc, save_name):

    fig, axs = plt.subplots(1, len(picks), sharex=True, sharey=True)
    for idx, pick in enumerate(picks):
        ax = axs[idx] if len(picks) == 2 else axs
        if isinstance(sensor_data, mne.time_frequency.AverageTFR):
            sensor_array = sensor_data.copy().pick(picks=pick).data.mean(axis=2)
            freq_array = sensor_data.freqs
            title_id = sensor_data.method.split('-')[1]
        else:
            freq_array = freqs[idx]
            sensor_array = sensor_data[idx]
            sensor_array /= sensor_array.mean()
            title_id = 'PSD'

        ax.plot(freq_array, sensor_array.T)
        ax.set_title(pick.upper())
        ax.set_xlabel('Frequency [Hz]')

    fig.suptitle(f'Sensor space {title_id}')
    fig.savefig(join(save_loc, save_name))
    plt.close(fig)



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


def add_to_sensor_space_report(subject, condition, sensor_subdir, sensor_tfr_plot_name, sensor_psd_plot_name,
                               tfr_temporal_dict, report_dir, report_name):
    i_o.check_and_build_subdir(report_dir)
    report_path = join(report_dir, report_name) # full path to report's location
    sensor_report = mne.open_report(report_path) # load report

    t_start = int(tfr_temporal_dict['t_start']* 1000)
    t_end = int(tfr_temporal_dict['t_end']* 1000)

    # find and load corresponding images...
    images_dict = {'PSD': i_o.find_file_matches(sensor_subdir, sensor_psd_plot_name),
                   'TFR': i_o.find_file_matches(sensor_subdir, sensor_tfr_plot_name.replace('filler', 'TFR')),
                   'ITC': i_o.find_file_matches(sensor_subdir, sensor_tfr_plot_name.replace('filler', f'{t_start}_{t_end}_ITC'))}

    for fig_type, fig_matches in images_dict.items():
        if not fig_matches:
            continue
        section = f'{condition}_{fig_type}'
        sensor_report.add_images_to_section(join(sensor_subdir, fig_matches[0]), captions=subject, section=section, scale=3)

    sensor_report.save(report_path, open_browser=False, overwrite=True)


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
