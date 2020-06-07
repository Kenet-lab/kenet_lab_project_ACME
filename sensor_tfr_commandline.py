import paradigm_config_mod as tacr_cfg
import sys
sys.path.insert(0, tacr_cfg.shared_func_dir)
import mne
import json
import logging
import argparse
import io_mod as i_o
import analysis as anal
from os.path import join


def main(subject, subject_fnames, log):
    logging.basicConfig(filename=log, level=logging.DEBUG)
    for subdir in ['epochs_subdir', 'epochs_sensor_subdir']:
        i_o.check_and_build_subdir(subject_fnames[subdir])

    for condition_name, condition_info in tacr_cfg.conditions_dicts.items(): # read epochs around conditions/event IDs
        epoch_fname, sensor_tfr_fname, sensor_tfr_plot_fname = i_o.format_variable_names({'condition': condition_name},
                                                                                         subject_fnames['epoch'],
                                                                                         subject_fnames['sensor_tfr'],
                                                                                         subject_fnames['sensor_tfr_plot'])

        epochs = mne.read_epochs(join(subject_fnames['epochs_subdir'], epoch_fname),
                                 proj=tacr_cfg.epochs_parameters_dict['proj'], preload=True)

        power, itc = anal.calc_sensor_tfr(epochs, tacr_cfg.freqs, tacr_cfg.n_cycles, tacr_cfg.n_jobs,
                                           subject_fnames['epochs_sensor_subdir'], sensor_tfr_fname)
        # plot, save TFR figure(s) that we time-window
        anal.manipulate_sensor_tfr(itc, tacr_cfg.tfr_temporal_dict, subject_fnames['epochs_sensor_subdir'], sensor_tfr_plot_fname, tacr_cfg.eeg)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-subject', type=str, help='Subject ID')
    parser.add_argument('-log', type=str, help='Logging script file name')
    parser.add_argument('-fnames', type=json.loads, help='Subject file naming information')

    arguments = parser.parse_args()

    main(arguments.subject, arguments.fnames, arguments.log)
