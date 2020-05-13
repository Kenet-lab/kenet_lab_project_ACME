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
        sensor_itc_fname, agg_plot_fname, ch_plot_fname = \
            format_variable_names(replace_dict, epoch_pattern, prelim_analyses_subdir, preproc_subdir,
                                  sensor_itc_pattern, sensor_itc_agg_plot_pattern, sensor_itc_chs_plot_pattern)

        epochs = read_epochs(subject_preproc_subdir, subject_epoch_fname, epochs_parameters_dict['proj'])

        # plot evoked/averaged sensor data and save it, too
        plot_evoked_sensor(epochs, prelim_analyses_subdir, evoked_sensor_pattern)
        # calculate itc, and save matrix
        itc = calc_sensor_itc(epochs, freqs, n_cycles, n_jobs, subject_prelim_analyses_subdir, sensor_itc_fname)

        # plot, save ITC figure(s) that we time-window
        manipulate_sensor_itc(itc, itc_params_dict, subject_prelim_analyses_subdir, agg_plot_fname, ch_plot_fname, eeg)
