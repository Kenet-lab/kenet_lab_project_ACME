import mne
from os.path import join
from io_mod import *
from preprocessing import *
from visuals import *
from tacvib_config_mod import *

logging.basicConfig(filename=sensor_space_script_log_name, level=logging.DEBUG)
for subject in get_subject_ids(get_subjects(paradigm_dir)):

    subject_paradigm_dir = join(paradigm_dir, subject)

    for condition_name, condition_info in conditions_dicts.items():
        replace_dict = {'subject': subject, 'condition': condition_name}

        subject_epoch_fname, subject_prelim_analyses_subdir, subject_preproc_subdir,\
        sensor_tfr_fname, agg_plot_fname, ch_plot_fname = \
            format_variable_names(replace_dict, epoch_pattern, prelim_analyses_subdir, preproc_subdir,
                                  sensor_tfr_pattern, sensor_tfr_agg_plot_pattern, sensor_tfr_chs_plot_pattern)

        epochs = mne.read_epochs(join(subject_preproc_subdir, subject_epoch_fname),
                                 proj=epochs_parameters_dict['proj'], preload=True)

        # calculate itc and power, save matrices
        power, itc = calc_sensor_tfr(epochs, freqs, n_cycles, n_jobs, subject_prelim_analyses_subdir, sensor_tfr_fname)
        # plot, save ITC figure(s) that we time-window
        manipulate_sensor_tfr(itc, tfr_temporal_dict, subject_prelim_analyses_subdir,
                              agg_plot_fname, ch_plot_fname, eeg)
