import paradigm_config as para_cfg
import mne
import logging
import io_helpers as i_o
import analysis as anlys
import visuals as vis
from os.path import join


def main(subject, subject_fnames, log):
    logging.basicConfig(filename=log, level=logging.DEBUG)
    for subdir in ['epochs_subdir', 'epochs_sensor_subdir']:
        i_o.check_and_build_subdir(subject_fnames[subdir])

    for condition_name, condition_info in para_cfg.conditions_dicts.items(): # read epochs around conditions/event IDs
        epoch_fname, evoked_fname, sensor_tfr_fname, sensor_tfr_plot_fname = i_o.format_variable_names({'condition': condition_name},
                                                                                                       subject_fnames['epoch'],
                                                                                                       subject_fnames['evoked'],
                                                                                                       subject_fnames['sensor_tfr'],
                                                                                                       subject_fnames['sensor_tfr_plot'],
                                                                                                       subject_fnames['evoked_plot'])

        epochs = mne.read_epochs(join(subject_fnames['epochs_subdir'], epoch_fname),
                                 proj=para_cfg.epochs_parameters_dict['proj'], preload=True)
        evoked = epochs.average(method='average')
        evoked.save(join(subject_fnames['epochs_subdir'], evoked_fname))

        anlys.calc_sensor_tfr(epochs, para_cfg.freqs, para_cfg.n_cycles, para_cfg.n_jobs,
                             subject_fnames['epochs_sensor_subdir'], sensor_tfr_fname, para_cfg.paradigm)
        anlys.compute_psd(evoked, para_cfg.freqs ,para_cfg.n_jobs, subject_fnames['epochs_sensor_subdir'], sensor_psd_fname=)

        anlys.analyze_sensor_space_and_add_to_report(subject, condition_name, subject_fnames['epochs_sensor_subdir'], )




        # plot, save TFR figure(s) that we time-window
        anlys.analyze_sensor_tfr(itc, para_cfg.tfr_temporal_dict, subject_fnames['epochs_sensor_subdir'], sensor_tfr_plot_fname)

        vis.make_report_sensor_space(subject, condition_name, subject_fnames['epochs_sensor_subdir'], subject_fnames['sensor_tfr_plot'],
                                     para_cfg.reports_dir, para_cfg.sensor_report_fname, para_cfg.tfr_temporal_dict)
