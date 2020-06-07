from os.path import join
from numpy import arange
from multiprocessing import cpu_count

### TOP LEVEL ### variables, locations independent of paradigm
transcend_dir = '/autofs/cluster/transcend'

meg_dir = join(transcend_dir, 'MEG') # MEG directory
erm_dir = join(meg_dir, 'erm') # MEG empty room recordings directory

subjects_dir = join(transcend_dir, 'MRI', 'WMA', 'recons') # MRI directory
# DPK - why "steven_scripts" rather than something generic.
shared_func_dir = join(transcend_dir, 'scripts', 'MEG', 'steven_scripts')

n_jobs = cpu_count() - 4

### MID LEVEL ### paradigm-relevant parameters, variables...
paradigm = 'tac_vib_only'
paradigm_dir = join(meg_dir, paradigm)

eeg = True

conductivity_no_eeg = (0.3,)
conductivity_eeg = (0.3, 0.006, 0.3)
conductivity = conductivity_no_eeg if not eeg else conductivity_eeg # three layers if EEG

# noise covariance matrix, inverse computation done by using either baseline period or ERM
proc_using_baseline = True
proc_using_erm = False if proc_using_baseline else True

# anatomical ROI
parc = 'aparc'
roi_list_anatomical = {'soma-lh': ['postcentralparietal-lh'],
                       'soma-rh': ['postcentralparietal-rh']}

functional_label_threshold_list = [0.5, 0.6, 0.7, 0.8, 0.9] # functional labels thresholds for activity

### LOW LEVEL ### analysis-relevant parameters, variables, etc...
# bandpass filtering
l_freq = 1.
h_freq = 144.

# merged/specified/grouped event IDs, conditions
conditions_dicts = {'25Hz': {'event_id': [1], # key <-> condition name
                            'value': 25.}, # value <-> condition's information (nested dictionary)
                    'baseline': {'event_id': None,
                                 'value': None}}

# artifact removal method(s)
preproc_ssp = True
preproc_ica = False if preproc_ssp else True # eventually add infrastructure to handle both methods simultaneously

# epoching parameters
#epoch_tmin = 0.2
epoch_tmin = 0.
epoch_tmax = 1.3
epoch_baseline = (-0.2, 0.)
epoch_proj = True if preproc_ssp else False

grad_epoch_reject = 5000e-13
mag_epoch_reject = 4e-12
eeg_epoch_reject = 120e-6
epoch_reject = dict(grad=grad_epoch_reject, mag=mag_epoch_reject, eeg=eeg_epoch_reject)
epochs_parameters_dict = {'tmin': epoch_tmin, 'tmax': epoch_tmax,
                          'baseline': epoch_baseline, 'proj': epoch_proj,
                          'reject': epoch_reject}

# parameters dictionary for windowing power/ITC, include modes like 'mean', 'max'...
freqs = arange(7, 99, 2) # frequencies of interest
n_cycles = freqs / 2.  # different number of cycles per frequency
n_cycles[freqs < 15] = 2

tfr_t_start = 0.4
tfr_t_end = 1.0
tfr_sliding = False
tfr_temporal_dict = {'t_start':tfr_t_start, 't_end': tfr_t_end,
                     'sliding': tfr_sliding} # if True, supply additional parameters
