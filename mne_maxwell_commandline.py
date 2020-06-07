import paradigm_config_mod as tacr_cfg
#import paradigm_config_mod as paradigm_cfg
import sys
sys.path.insert(0, tacr_cfg.shared_func_dir)
import json
import logging
import argparse
import io_mod as i_o
import preprocessing as preproc
import maxwell_filter_config as sss_cfg
from os.path import join


def handle_erm(raw, subject_erm_dir, raw_erm_fname, erm_sss_pattern): # return ERM file locations, directory information
    date_paradigm = i_o.read_measure_date(raw.info)
    subject_erm_date_dir = join(subject_erm_dir, date_paradigm)

    raw_erm = i_o.preload_raws(subject_erm_date_dir, raw_erm_fname) # load the raw ERM data
    erm_sss_fname = i_o.format_variable_names({'date': date_paradigm}, erm_sss_pattern)
    return raw_erm, erm_sss_fname


def main(subject, subject_fnames, log):
    logging.basicConfig(filename=log, level=logging.DEBUG)

    subject_paradigm_dir = join(tacr_cfg.paradigm_dir, subject)
    subject_erm_dir = join(tacr_cfg.erm_dir, subject)
    subject_sss_params = sss_cfg.sss_params # load SSS parameters dictionary

    i_o.check_and_build_subdir(subject_fnames['preproc_subdir']) # check and/or build subject subdirectories relevant to the script

    raw = i_o.preload_raws(subject_paradigm_dir, subject_fnames['raw_paradigm'])

    subject_sss_params['destination'] = raw.info['dev_head_t'] # update SSS parameters dictionary with subject-specific values
    subject_sss_params['origin'] = preproc.generate_head_origin(raw.info, subject_paradigm_dir, subject_fnames['head_origin'])
    subject_sss_params['head_pos'] = preproc.calc_head_position(raw, subject_fnames['preproc_subdir'], subject_fnames['head_pos'])

    raw, bads_meg = preproc.find_bads_meg(raw, subject_sss_params, subject_fnames['preproc_subdir'], subject_fnames['meg_bads'], tacr_cfg.n_jobs)
    sss = preproc.mne_maxwell_filter_paradigm(raw, subject_sss_params, subject_fnames['preproc_subdr'], subject_fnames['sss_paradigm'])

    if tacr_cfg.proc_using_erm:
        raw_erm, erm_sss_fname = handle_erm(raw, subject_erm_dir, subject_fnames['raw_erm'], subject_fnames['sss_erm'])
        erm_sss = preproc.mne_maxwell_filter_erm(raw_erm, bads_meg, subject_sss_params, subject_fnames['preproc_subdir'], erm_sss_fname)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-subject', type=str, help='Subject ID')
    parser.add_argument('-log', type=str, help='Logging script file name')
    parser.add_argument('-fnames', type=json.loads, help='Subject file naming information')

    arguments = parser.parse_args()

    main(arguments.subject, arguments.fnames, arguments.log)
