# SSP parameters
n_grad_ssp = 2
n_mag_ssp = 2
n_eeg_ssp = 2
average_ssp = True
ssp_params_dict = {'n_grad': n_grad_ssp, 'n_mag': n_mag_ssp, 'n_eeg': n_eeg_ssp, 'average': average_ssp}

# ICA parameters
n_comps_ica = 0.999
fit_method_ica = 'fastica'
random_state_ica = 42
ica_params_dict = {'n_components': n_comps_ica, 'fit_method': fit_method_ica, 'random_state': random_state_ica}
