"""
Artifact removal configuration file
Holds parameters used in SSP and ICA methods to remove eye blinks and heart beats
"""
from os.path import join
import paradigm_config as para_cfg

# SSP parameters
n_grad_ssp = 2
n_mag_ssp = 2
n_eeg_ssp = 1
average_ssp = True
# in the case of missing ExG electrodes/channels, supply MEEG channels to detect artifacts
ecg_fab_chs = ['MEG1531', 'MEG2631', 'MEG1541', 'MEG2621']
eog_fab_chs = ['EEG001', 'EEG002', 'EEG003', 'EEG005', 'EEG006', 'EEG007', 'EEG008',
               'MEG1213', 'MEG1422']

ssp_params_dict = {'n_grad': n_grad_ssp, 'n_mag': n_mag_ssp, 'n_eeg': n_eeg_ssp, 'average': average_ssp}
ssp_dict = {'params': ssp_params_dict, 'ecg_fab_channels': ecg_fab_chs, 'eog_fab_channels': eog_fab_chs}

# ICA parameters
n_comps_ica = 0.999
fit_method_ica = 'fastica'
random_state_ica = 42
ica_params_dict = {'n_components': n_comps_ica, 'fit_method': fit_method_ica, 'random_state': random_state_ica}

artifact_removal_vars_output_filename = f'{para_cfg.paradigm}_sss_config_variables_output_{para_cfg.current_datetime}.txt'
with open(join(para_cfg.paradigm_dir, artifact_removal_vars_output_filename), 'w+') as var_output:
    for var_name, value in dict(vars()).items():
        var_output.write(f'{var_name}: {value}\n')
var_output.close()