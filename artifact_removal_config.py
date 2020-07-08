"""
Artifact removal configuration file
Holds parameters used in SSP and ICA methods to remove eye blinks and heart beats
"""
from os.path import join
import paradigm_config_mod as para_cfg

# SSP parameters
n_grad_ssp = 2
n_mag_ssp = 2
n_eeg_ssp = 1
average_ssp = True

frontal_channels_many = ['MEG0111', 'MEG0121', 'MEG0131', 'MEG0211', 'MEG0221', 'MEG0231',
                        'MEG0311', 'MEG0321', 'MEG0331', 'MEG1511', 'MEG1521', 'MEG1531',
                        'EEG001', 'EEG002', 'EEG003', 'EEG004', 'EEG005', 'EEG006', 'EEG007', 'EEG008', 'EEG061', 'EEG062']

frontal_channels = ['EEG061,EEG062', 'EEG001,EEG002', 'MEG0122,MEG1412', 'MEG0313,MEG1213']
ssp_params_dict = {'n_grad': n_grad_ssp, 'n_mag': n_mag_ssp, 'n_eeg': n_eeg_ssp, 'average': average_ssp}
ssp_dict = {'params': ssp_params_dict, 'frontal_channels': frontal_channels}

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