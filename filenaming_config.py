from enum import Enum
import paradigm_config_mod as paradigm_cfg
import sys
sys.path.insert(0, paradigm_cfg.shared_func_dir)
import io_mod as i_o
from os.path import join
from time import strftime


class Sentinel(Enum):
    """Success sentinels for the various stages of processing."""
    MAXWELL = "maxwell_success"
    EPOCH = "epoch_success"
    SENSORS_TFR = "sensor_tfr_success"

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

def create_paradigm_subject_mapping(subject):
    """ Create a dictionary whose keys are the paradigm's subjects and
        whose values are nested dictionaries of their filenames.
    """
    subject_paradigm_tag = f'{subject}_{paradigm}'
    subject_paradigm_dir = join(paradigm_dir, subject)

    subject_filenames_dict = {}

    # DPK - sentinel file locations.  Change these to whatever makes
    # sense for your file layout.
    subject_filenames_dict[Sentinel.MAXWELL] = join(subject_paradigm_dir, Sentinel.MAXWELL.value)
    subject_filenames_dict[Sentinel.EPOCH] = join(subject_paradigm_dir, Sentinel.EPOCH.value)
    subject_filenames_dict[Sentinel.SENSORS_TFR] = join(subject_paradigm_dir, Sentinel.SENSORS_TFR.value)

    subject_filenames_dict['epochs_subdir'] = join(subject_paradigm_dir, 'visit_date', 'epoched')
    subject_filenames_dict['preproc_subdir'] = join(subject_paradigm_dir, 'visit_date', 'preprocessing')

    subject_filenames_dict['epochs_sensor_subdir'] = join(subject_filenames_dict['epochs_subdir'], 'sensor_space')
    subject_filenames_dict['preproc_plots_subdir'] = join(subject_filenames_dict['preproc_subdir'], 'plots')

    subject_filenames_dict['raw_paradigm'] = f'{subject}_{paradigm}*_raw.fif'
    subject_filenames_dict['sss_paradigm'] = '_'.join((subject_paradigm_tag, 'date_sss_raw.fif'))

    subject_filenames_dict['meg_bads'] = '_'.join((subject_paradigm_tag, 'bad_channels_meg.txt'))
    subject_filenames_dict['eeg_bads'] = '_'.join((subject_paradigm_tag, 'bad_channels_eeg.txt'))

    subject_filenames_dict['head_origin'] = '_'.join((subject_paradigm_tag, 'head_origin_coordinates.txt'))
    subject_filenames_dict['head_pos'] = '_'.join((subject_paradigm_tag, 'head_position.txt'))

    subject_filenames_dict['raw_erm'] = f'{subject}_erm_*raw.fif'
    subject_filenames_dict['sss_erm'] = '_'.join((subject_paradigm_tag, 'erm_date_sss_raw.fif'))

    subject_filenames_dict['proj'] = '_'.join((subject_paradigm_tag, proj_ext))
    subject_filenames_dict['ssp_topo'] = '_'.join((subject_paradigm_tag, ssp_topo_ext))

    subject_filenames_dict['filt_paradigm'] = '_'.join((subject_paradigm_tag, filt_ext))

    subject_filenames_dict['epoch'] = '_'.join((subject_paradigm_tag, epoch_ext))
    subject_filenames_dict['sensor_tfr'] = '_'.join((subject_paradigm_tag, sensor_tfr_ext))

    subject_filenames_dict['sensor_tfr_plot'] = '_'.join((subject_paradigm_tag, sensor_tfr_plot_ext))
    subject_filenames_dict['evoked_plot'] = '_'.join((subject_paradigm_tag, sensor_evoked_ext))

    return subject_filenames_dict
