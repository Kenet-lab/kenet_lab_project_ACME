import paradigm_config_mod as paradigm_cfg
import sys
sys.path.insert(0, paradigm_cfg.shared_func_dir)
import io_mod as i_o
from os.path import join
from time import strftime

### TOP LEVEL: HARD-CODED LOCATIONS
current_datetime = strftime('%Y%m%d-%H%M%S')
meg_dir = paradigm_cfg.meg_dir # MEG directory

### MID LEVEL:
paradigm = paradigm_cfg.paradigm # paradigm definition
paradigm_dir = join(meg_dir, paradigm) # build the paradigm directory

### LOW LEVEL: filenaming and breadcrumbs
proj_ext = 'date_kind-proj.fif'
ssp_topo_ext = proj_ext.replace('.fif', '_topomap.png')

filt_ext = f'date_{paradigm_cfg.l_freq}hp_{paradigm_cfg.h_freq}lp_sss_raw.fif'

epoch_ext = filt_ext.replace('raw', 'condition-epo')
sensor_evoked_ext = filt_ext.replace('raw.fif', 'condition-evoked_filler.png')
sensor_tfr_ext = filt_ext.replace('raw.fif', 'condition-tfr_kind-tfr.h5')

sensor_tfr_plot_ext = sensor_tfr_ext.replace('-tfr.h5', '_filler.png')

# script log filenames
maxwell_script_log_name = f'{paradigm}_maxwell_script_{current_datetime}.log'
epoched_script_log_name = f'{paradigm}_epoch_script_{current_datetime}.log'
sensor_space_script_log_name = f'{paradigm}_sensor_space_script_{current_datetime}.log'

""" create a dictionary whose keys are the paradigm's subjects
                        whose values are nested dictionaries of their filenames """
subjects_filenames_dicts = {}
for subject in i_o.get_subject_ids(i_o.get_subjects(paradigm_dir)):

    subject_paradigm_tag = f'{subject}_{paradigm}'
    subject_paradigm_dir = join(paradigm_dir, subject)

    subjects_filenames_dicts[subject] = {}

    subjects_filenames_dicts[subject]['epochs_subdir'] = join(subject_paradigm_dir, 'visit_date', 'epoched')
    subjects_filenames_dicts[subject]['preproc_subdir'] = join(subject_paradigm_dir, 'visit_date', 'preprocessing')

    subjects_filenames_dicts[subject]['epochs_sensor_subdir'] = join(subjects_filenames_dicts[subject]['epochs_subdir'], 'sensor_space')
    subjects_filenames_dicts[subject]['preproc_plots_subdir'] = join(subjects_filenames_dicts[subject]['preproc_subdir'], 'plots')

    subjects_filenames_dicts[subject]['raw_paradigm'] = f'{subject}_{paradigm}*_raw.fif'
    subjects_filenames_dicts[subject]['sss_paradigm'] = '_'.join((subject_paradigm_tag, 'date_sss_raw.fif'))

    subjects_filenames_dicts[subject]['meg_bads'] = '_'.join((subject_paradigm_tag, 'bad_channels_meg.txt'))
    subjects_filenames_dicts[subject]['eeg_bads'] = '_'.join((subject_paradigm_tag, 'bad_channels_eeg.txt'))

    subjects_filenames_dicts[subject]['head_origin'] = '_'.join((subject_paradigm_tag, 'head_origin_coordinates.txt'))
    subjects_filenames_dicts[subject]['head_pos'] = '_'.join((subject_paradigm_tag, 'head_position.txt'))

    subjects_filenames_dicts[subject]['raw_erm'] = f'{subject}_erm_*raw.fif'
    subjects_filenames_dicts[subject]['sss_erm'] = '_'.join((subject_paradigm_tag, 'erm_date_sss_raw.fif'))

    subjects_filenames_dicts[subject]['proj'] = '_'.join((subject_paradigm_tag, proj_ext))
    subjects_filenames_dicts[subject]['ssp_topo'] = '_'.join((subject_paradigm_tag, ssp_topo_ext))

    subjects_filenames_dicts[subject]['filt_paradigm'] = '_'.join((subject_paradigm_tag, filt_ext))

    subjects_filenames_dicts[subject]['epoch'] = '_'.join((subject_paradigm_tag, epoch_ext))
    subjects_filenames_dicts[subject]['sensor_tfr'] = '_'.join((subject_paradigm_tag, sensor_tfr_ext))

    subjects_filenames_dicts[subject]['sensor_tfr_plot'] = '_'.join((subject_paradigm_tag, sensor_tfr_plot_ext))
    subjects_filenames_dicts[subject]['evoked_plot'] = '_'.join((subject_paradigm_tag, sensor_evoked_ext))
