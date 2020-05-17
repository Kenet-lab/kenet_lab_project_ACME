from os.path import join
from numpy import arange
from multiprocessing import cpu_count
from time import strftime
current_datetime = strftime('%Y%m%d-%H%M%S')

### TOP LEVEL ### variables, locations independent of paradigm
transcend_dir = '/autofs/cluster/transcend'

shared_func_dir = join(transcend_dir, 'scripts', 'MEG', 'steven_scripts')
meg_dir = join(transcend_dir, 'MEG') # MEG directory

erm_dir = join(meg_dir, 'erm') # MEG empty room recordings directory
subjects_dir = join(transcend_dir, 'MRI', 'WMA', 'recons') # MRI directory

n_jobs = cpu_count() - 4

### MID LEVEL ### paradigm-relevant parameters, variables...
eeg = True
conductivity = (0.3,) if not eeg else (0.3, 0.006, 0.3) # three layers if EEG

paradigm = 'tacvib'
paradigm_dir = join(meg_dir, paradigm)

scripts_dir = join(meg_dir, 'tacvib_scripts_mod')

artifact_eval_subdir = join(paradigm_dir, 'subject', 'artifact_removal')
labels_subdir = join(paradigm_dir, 'subject', 'labels')
prelim_analyses_subdir = join(paradigm_dir, 'subject', 'preliminary_analyses')
preproc_subdir = join(paradigm_dir, 'subject', 'preprocessing')

# noise covariance matrix, inverse computation done by using either baseline period or ERM
proc_using_baseline = True
proc_using_erm = False if proc_using_baseline else True

# anatomical ROI
parc = 'aparc'
roi_list_anatomical = {'AUD-lh': ['transversetemporal-lh', 'superiortemporal-lh'],
                       'AUD-rh': ['transversetemporal-rh', 'superiortemporal-rh'],
                        'AUD_small-lh': ['transversetemporal-lh'],
                        'AUD_small-rh': ['transversetemporal-rh'] }

# functional labels
functional_label_threshold_list = [0.5, 0.6, 0.7, 0.8, 0.9]

### LOW LEVEL ### analysis-relevant parameters, variables, etc...
reports_dir = join(paradigm_dir, 'reports')
results_dir = join(paradigm_dir, 'results')

meg_bad_channel_pattern = 'subject_bad_channels_meg.txt'
eeg_bad_channel_pattern = 'subject_bad_channels_eeg.txt'
head_origin_pattern = 'subject_head_origin_coordinates.txt'

raw_pattern = 'subject_tac_vib_only_raw.fif'
sss_pattern = 'subject_tac_vib_sss_raw.fif'

erm_pattern = 'subject_erm_*raw.fif'
erm_sss_pattern = 'subject_erm_paradigm_date_raw.fif'

proj_pattern = 'subject_kind-proj.fif'
ssp_topo_pattern = 'subject_kind_proj_topomap.png'
evoked_sensor_pattern = 'subject_sensor_evoked_fignum-plot.png'
sensor_tfr_pattern = 'subject_sensor_kind-tfr.h5'

sensor_tfr_agg_plot_pattern = 'subject_condition_channels_aggregate_sensor_kind.png'
sensor_tfr_chs_plot_pattern = 'subject_condition_channels_'

sensor_itc_agg_plot_pattern = 'subject_condition_channel_type_aggregate_sensor_itc.png'
sensor_itc_chs_plot_pattern = 'subject_condition_channel_type_channels_sensor_itc.png'

# bandpass filtering
l_freq = 1.
h_freq = 144.

# artifact removal method(s)
preproc_ssp = True
preproc_ica = False if preproc_ssp else True # eventually add infrastructure to handle both methods simultaneously

ssp_params_dict = {'n_grad': 2, 'n_mag': 2, 'n_eeg': 2, 'average': True}
ica_params_dict = {'n_components': 0.999, 'fit_method': 'fastica', 'random_state': 42}

freqs = arange(7, 99, 2) # frequencies of interest
n_cycles = freqs / 2.  # different number of cycles per frequency
n_cycles[freqs < 15] = 2

# merged/specified/grouped event IDs, conditions
conditions_dicts = {'25Hz': {'event_id': [1], # key <-> condition name
                            'value': 25.}, # value <-> condition's information (nested dictionary)
                    'baseline': {'event_id': None,
                                 'value': None}}

# epoching parameters
epochs_parameters_dict = {'tmin': 0.2, 'tmax': 1.3,
                          'baseline': (-0.1, 0.), 'proj': True if preproc_ssp else False,
                          'reject': dict(grad=5000e-13, mag=4e-12, eeg=40e-6)}

epoch_pattern = 'subject_condition-epo.fif'

# parameters dictionary for windowing power/ITC, include modes like 'mean', 'max'...
tfr_temporal_dict = {'t_start': 0.4, 't_end': 1.0,
                     'sliding': False} # if True, supply additional parameters

# script log filenames
maxwell_script_log_name = 'tacvib_maxwell_script_{}.log'.format(current_datetime)
epoching_script_log_name = 'tacvib_epoch_script_{}.log'.format(current_datetime)
sensor_space_script_log_name = 'tacvib_sensor_space_script_{}'.format(current_datetime)
