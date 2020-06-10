from os.path import join, split, isdir
from os import walk, listdir, mkdir, rename
from shutil import copyfile
import pandas as pd
from datetime import datetime
import mne
import fnmatch
import logging
from requests import post
import io_mod as i_o

paradigms = ['AttenVis', 'AttenAud']

MEG_dir = '/autofs/cluster/transcend/MEG'
megraid_dir = '/autofs/space/megraid_research/MEG/tal'
erm_dir = '/autofs/cluster/transcend/MEG/erm'


def check_or_build_dir(path, subdir):
    if not isdir(join(path, subdir)):
        mkdir(join(path, subdir))
    return


def list_filepaths(dir):
    all_filepaths = []
    for root, dirs, files in walk(dir):
        for name in files:
            all_filepaths.append(join(root, name))
    return all_filepaths


def filter_subjects_megraid(megraid_dir):
    # filter subjects that do not follow subject ID naming convention
    keep = []
    for subject in megraid_dir:
        try:
            sid = subject.split('_')[1]
        except:
            continue
        if sid.isnumeric() and len(sid) > 5:
            keep.append(subject)
        elif 'AC' in sid.upper():
            keep.append(subject)
    return keep


def get_measure_date_from_path(path, pattern):
    """
    :param path: string denoting the path to the file that we will read the information header from
    :param pattern: string denoting the file's name that we wish to read information from
    :return: visit date as a string (YYYYMMDD)
    """
    info_files = find_file_matches(path, pattern)
    info = mne.io.read_info(join(path, info_files[0]), verbose=False)
    return read_measure_date(info)


def collect_paradigm_files(paradigm, subject_files):
    paradigm_files = [f for f in subject_files if paradigm in f]
    if len(paradigm_files) > 0:
        return paradigm_files
    else:
        return None

def collect_dates(files_list):
    dates = [split(f)[0].split('/')[-1] for f in files_list]
    uniques = list(set(dates))
    return sorted(uniques) # earliest to most recent

def list_matches(files_list1, files_list2):
    # see what two lists of files have in common
    matches = set(files_list1) & set(files_list2)
    return matches

def list_mismatches(files_list1, files_list2):
    mismatches = set(files_list1).difference(files_list2)
    return mismatches

