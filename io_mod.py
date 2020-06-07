import mne
import fnmatch
import logging
import numpy as np
from os.path import join, isdir
from os import mkdir, listdir


def find_file_matches(loc, pattern):
    """
    :param loc: string denoting where file(s) may be found
    :param pattern: string to identify file(s) specified by it
    :return: list of file(s) found matching a given pattern, in a given location
    """
    files_matching_pattern = fnmatch.filter(listdir(loc), pattern)
    file_matches = [] if len(files_matching_pattern) == 0 else files_matching_pattern
    logging.info(f'The following {len(file_matches)} were found matching the pattern {pattern} in {loc}:\n{listdir(loc)}')
    return file_matches


def preload_raws(loc, pattern, concat=True):
    """
    :param loc: string denoting where raw file(s) may be found
    :param pattern: string to identify, match the correct file(s)
    :param concat: boolean keyword argument to turn on/off raw file concatenation (default True)
    :return: pre-loaded raw .fif file(s)
    """
    list_of_raws = find_file_matches(loc, pattern)
    try:
        raws = [mne.io.read_raw_fif(join(loc, fif), preload=True) for fif in list_of_raws]
    except TypeError:
        logging.info('Raw files failed to be read')
    raw = mne.io.concatenate_raws(raws) if concat else raws
    del raws
    return raw


def get_subject_id_from_data(data):
    """
    :param data: MNE object like raw, epochs, tfr,... that has an Info attribute
    :return: string denoting the subject ID
    """
    return data.info['subject_info']['his_id']


def find_events(raw, stim_channel):
    """
    :param raw: raw file whose info to parse
    :param stim_channel: string stimulus channel name
    :return: events
    :return: events baseline
    """
    events = mne.find_events(raw, stim_channel=stim_channel, shortest_event=1)
    events_baseline = make_events_baseline(events)
    return events, events_baseline


def make_events_baseline(events, value=0):
    """
    set the baseline of the trigger channel to a specified value
    :param events: mne Events
    :param value: value to set baseline events to (usually zero)
    :return: events baseline
    """
    events_baseline = events.copy()
    events_baseline[:, 2] = events[:, 2] - events[:, 1]
    events_baseline[:, 1] = np.zeros(len(events[:, 1])) + value
    return events_baseline

def read_measure_date(info):
    """
    read measure date, convert to YYYYMMDD to find matching ERM file
    :param info: MNE info object
    :return: date (YYYYMMDD)
    """
    try:
        visit_datetime = info['meas_date']
    except KeyError:
        logging.info('Unable to parse measure timestamp from Info')
    return visit_datetime.strftime('%Y%m%d')


def read_proj(proj_loc, proj_pattern, kind):
    """
    :param kind: SSP projection channel kind (EOG, ECG)
    """
    replace_dict = {'kind': kind}
    proj_fname = format_variable_names(replace_dict, proj_pattern)
    return mne.read_proj(join(proj_loc, proj_fname))


def save_proj(projs, proj_save_loc, proj_fname, kind):
    """
    :param kind: SSP projection channel kind (EOG, ECG)
    """
    replace_dict = {'kind': kind}
    proj_save_name = format_variable_names(replace_dict, proj_fname)
    mne.write_proj(join(proj_save_loc, proj_save_name), projs)


def check_and_build_subdir(subdir): # needs work, should replace more than subject?
    """
    build subject-specific subdirectories
    :param subdir: subject specific subdirectory name
    :param subject: subject ID
    """
    if not isdir(subdir):
        mkdir(subdir)
        logging.info(f'{subdir} created')


def save_epochs(epochs, condition_name, save_loc, epoch_pattern):
    """save epoch files"""
    epoch_fname = format_variable_names({'condition': condition_name}, epoch_pattern)
    epochs.save(join(save_loc, epoch_fname), overwrite=True)


def get_subjects(paradigm_dir):
    """ list the subjects in a paradigm directory"""
    return listdir(paradigm_dir)


def get_subject_ids(subjects):
    """ keep contents of paradigm directory if contents are subjects"""
    return [s for s in subjects if s.isnumeric()]


def get_eeg_inds(raw):
    """ locate the indices in the data corresponding to EEG channels
    :param raw: raw data
    """
    eeg_inds = mne.pick_types(raw.info, meg=False, eeg=True)
    return eeg_inds


def read_bad_channels_eeg(loc, eeg_bads_fname):
    eeg_bads_txt = open(join(loc, eeg_bads_fname))
    lines = eeg_bads_txt.readlines()
    eeg_bads = [line.strip() for line in lines]
    return eeg_bads


def read_sensor_itc(save_loc, subject, sensor_itc_pattern):
    replace_dict = {'subject': subject}
    itc_name = format_variable_names(replace_dict, sensor_itc_pattern)
    itc = mne.time_frequency.read_tfrs(join(save_loc, itc_name))
    return itc


def format_variable_names(replace_dict, *vars):
    """ format any number of variable names
    :param replace_dict: dictionary whose keys are values to replace and values are replacement values
    :param vars: any number of strings that we would like to replace values of"""
    return_list = [None] * len(vars)
    for i, var in enumerate(vars):
        for key, value in replace_dict.items():
            if key in var:
                var = var.replace(key, value)
            else:
                continue
        return_list[i] = var
    if len(vars) == 1:
        return return_list[0]
    else:
        return tuple(return_list)


def log_projs(projs, kind): # logging function for SSP projection information
    # *** what more could I log?
    if projs: # projections were found and added
        logging.info('Projections ({}) found:\n {}'.format(kind, projs))
    else: # no projections found or added
        logging.info('No {} projections added or found'.format(kind))


def log_epochs(epochs): # logging function for epoch data information
    logging.info(f'General epoch information:\n{epochs}')
    logging.info(f'Detailed view:\n{epochs.info}')


def headpositions_match(raws):
    """
    check if device head transformations match between multiple runs of a paradigm
    NOTE: function assumes the correct head position is the first run's head position, ask Tal + Seppo if this is the case
    :param raws: raw .fif files
    :return: bool True (head positions match), False (do not match)
    """
    match = True
    for i, raw in enumerate(raws):
        if not np.allclose(raws[0].info['dev_head_t'], raw.info['dev_head_t']):
            match = False
        else: # FIX THIS CODE
            logging.error('head positions do not match between:\n {}\n{}'.format(raws[0], raws[i]))
            continue
    return match
