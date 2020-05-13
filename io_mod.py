import fnmatch
import logging
import mne
from os.path import join, isdir
from os import mkdir, listdir
import numpy as np
from datetime import datetime


def find_file_matches(loc, pattern):
    """
    :param loc: string denoting where file(s) may be found
    :param pattern: string to identify file(s) specified by it
    :return: file(s) found matching a given pattern, in a given location
    """
    files = fnmatch.filter(listdir(loc), pattern)
    if len(files) == 0:
        logging.error('No files matching pattern {} were found in {}'.format(pattern, loc))
        return None
    else:
        return files.sort()

def preload_raws(loc, pattern, concat=True):
    """
    :param loc: string denoting where raw file(s) may be found
    :param pattern: string to identify, match the correct file(s)
    :param concat: boolean keyword argument to turn on/off raw file concatenation (default True)
    :return: pre-loaded raw .fif file(s)
    """
    fifs = find_file_matches(loc, pattern)
    if fifs: # found
        raws = [mne.io.read_raw_fif(join(loc, fif), preload=False) for fif in fifs]
        if len(fifs) > 1:
            return raws[0]
        elif concat:
            return mne.io.concatenate_raws(raws)
        else:
            return raws
    else:
        return


def get_subject_id_from_data(data):
    """
    :param data: MNE object like raw, epochs, tfr,... that has an Info attribute
    """
    subject_id = data.info['subject_info']['his_id']
    return subject_id

def check_headpositions_match(raws):
    """
    check if device head transformations match between multiple runs of a paradigm
    NOTE: function assumes the correct head position is the first run's head position, ask Tal + Seppo if this is the case
    :param raws: raw .fif files
    :return: bool True (there is a mismatch) or False (no mismatch)
    """
    match = True
    for i, raw in enumerate(raws):
        if not np.allclose(raws[0].info['dev_head_t'], raw.info['dev_head_t']):
            match = False
        else:
            logging.error('head positions do not match between:\n {}\n{}'.format(raws[0], raws[i]))
            continue
    return match


def find_events(raw, stim_channel):
    """
    :param raw: raw file whose info to parse
    :param stim_channel: string stimulus channel name
    :return: events
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
    read measure date, convert to YYMMDD to find matching ERM file
    :param info: MNE info object
    :return: date (YYMMDD) as a string
    """
    try:
        ts = info['meas_date'][0]
        date = datetime.utcfromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
        date = date.split(' ')[0]  # just want YYMMDD
        measure_date = date.replace('-', '')
        return measure_date
    except:
        logging.error('Unable to parse measure timestamp from Info')
        return

def save_head_origin(head_origin, save_loc, head_origin_fname):
    """
    :param head_origin: array containing [x y z] coordinates in millimeters
    """
    np.savetxt(join(save_loc, head_origin_fname), head_origin)
    return

def read_proj(proj_loc, proj_pattern, subject, kind):
    replace_dict = {'subject': subject, 'kind': kind}
    proj_fname = format_variable_names(replace_dict, proj_pattern)
    return mne.read_proj(join(proj_loc, proj_fname))

def save_proj(projs, proj_save_loc, proj_fname, kind):
    replace_dict = {'kind': kind}
    proj_save_name = format_variable_names(replace_dict, proj_fname)
    mne.write_proj(join(proj_save_loc, proj_save_name), projs)
    return

def check_and_build_subdir(subdir, subject): # needs work, should replace more than subject?
    """
    :param subdir: subject specific subdirectory name
    :param subject: subject ID
    """
    subject_subdir = subdir.replace('subject', subject)
    if not isdir(subject_subdir):
        mkdir(subject_subdir)
        logging.info('{} created'.format(subject_subdir))
    return

def save_epochs(epochs, condition_name, save_loc, epoch_pattern): # save epoch data
    replace_dict = {'subject': get_subject_id_from_data(epochs),
                    'condition': condition_name}
    epoch_fname = format_variable_names(replace_dict, epoch_pattern)
    epochs.save(join(save_loc, epoch_fname), overwrite=True)
    return

def read_epochs(saved_loc, epoch_fname, use_proj): # read epoch data
    epochs = mne.read_epochs(join(saved_loc, epoch_fname), proj=use_proj, preload=True)
    return epochs

def save_ica(ica, save_loc, fname): # save ICA model
    ica.save(join(save_loc, fname))
    return

def read_ica(saved_loc, fname): # read ICA model
    ica = mne.preprocessing.read_ica(join(saved_loc, fname))
    return ica

def get_subjects(paradigm_dir): # list the subjects in a paradigm directory
    # get subject ids fom the pardigm_dir subdirectory
    return listdir(paradigm_dir)

def get_subject_ids(subjects): # keep contents of paradigm directory if they are subjects
    return [s for s in subjects if s.isnumeric()]

def check_eeg_availability(raw): # return True/False if EEG channels exist in raw data
    eeg_inds = mne.pick_types(raw.info, meg=False, eeg=True)
    if len(eeg_inds) > 0:
        return True # EEG available
    else:
        return False

def get_eeg_inds(raw):
    eeg_inds = mne.pick_types(raw.info, meg=False, eeg=True)
    return eeg_inds

def read_bad_channels_eeg(loc, eeg_bads_fname):
    eeg_bads_txt = open(join(loc, eeg_bads_fname))
    lines = eeg_bads_txt.readlines()
    eeg_bads = [line.strip() for line in lines]
    return eeg_bads

def read_bad_channels_meg_elekta(loc, meg_bads_fname):
    meg_bads_txt = open(join(loc, meg_bads_fname))
    lines = meg_bads_txt.readlines()
    meg_bads = [line.strip() for line in lines]
    return meg_bads[0] # only difference between the above function is this line... change how MEG bads are written

def save_sensor_itc(itc, save_loc, sensor_itc_fname):
    itc.save(join(save_loc, sensor_itc_fname))
    return

def read_sensor_itc(save_loc, subject, sensor_itc_pattern):
    replace_dict = {'subject': subject}
    itc_name = format_variable_names(replace_dict, sensor_itc_pattern)
    itc = mne.time_frequency.read_tfrs(join(save_loc, itc_name))
    return itc

def format_variable_names(replace_dict, *vars): # formats variable names
    return_list = [None] * len(vars)
    for i, var in enumerate(vars):
        for key, value in replace_dict.items():
            if key in var:
                var = var.replace(key, value)
            else:
                continue
        return_list[i] = var
    return tuple(return_list)

def log_projs(projs, kind): # logging function for SSP projection information
    # *** what more could I log?
    if projs: # projections were found and added
        logging.info('Projections ({}) found:\n {}'.format(kind, projs))
    else: # no projections found or added
        logging.info('No {} projections added or found'.format(kind))
    return


def log_epochs(epochs): # logging function for epoch data information
    logging.info('General epoch information:\n{}'.format(epochs))
    logging.info('Detailed view:\n{}'.format(epochs.info))
    return


