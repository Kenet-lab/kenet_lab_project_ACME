from os.path import join
import paradigm_config as para_cfg

neuromag_root = '/space/orsay/8/megdev/megsw-neuromag/databases'
# mne maxwell filtering - create maxwell_config to house these SSS parameters
cal = join(neuromag_root, 'sss', 'sss_cal.dat')
ctc = join(neuromag_root, 'ctc', 'ct_sparse.fif')
int_order = 8
ext_order = 3
st_dur = 10.
st_corr = 0.98
coord_frame = 'head'
regularize = 'in'
sss_params = {'calibration': cal, 'cross_talk': ctc,
              'int_order': int_order, 'ext_order': ext_order, 'st_duration': st_dur,
              'st_correlation': st_corr, 'coord_frame': coord_frame, 'regularize': regularize}

sss_vars_output_filename = f'{para_cfg.paradigm}_sss_config_variables_output_{para_cfg.current_datetime}.txt'
with open(join(para_cfg.paradigm_dir, sss_vars_output_filename), 'w+') as var_output:
    for var_name, value in dict(vars()).items():
        var_output.write(f'{var_name}: {value}\n')
var_output.close()