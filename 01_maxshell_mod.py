from os.path import join
from tacvib_config_mod import *
from io_mod import *
from preprocessing import *

def handle_erm(raw, subject_erm_dir, erm_pattern, ): # return ERM file locations, directory information

    date_paradigm = read_measure_date(raw.info) # match recording date to find the correct file
    subject_erm_date_dir = join(subject_erm_dir, date_paradigm)
    raw_erm_name = find_file_matches(subject_erm_date_dir, erm_pattern)[0]

    replace_dict.update({'paradigm_date': date_paradigm})
    erm_sss_name = format_variable_names(replace_dict, erm_sss_pattern)

    return date_paradigm, raw_erm_name, erm_sss_name


logging.basicConfig(filename=maxwell_script_log_name, level=logging.DEBUG)
for subject in get_subject_ids(get_subjects(paradigm_dir)):
    subject_paradigm_dir = join(paradigm_dir, subject) # locate subject's corresponding paradigm directory
    subject_erm_dir = join(erm_dir, subject) # locate subject's corresponding ERM directory

    # check and/or build relevant directories
    # could/should move this to the plotting module/script that is run before this script (not yet built)
    for subject_subdir in [artifact_eval_subdir, labels_subdir, prelim_analyses_subdir, preproc_subdir]:
        check_and_build_subdir(subject_subdir, subject)

    replace_dict = {'subject': subject} # format raw filename on a subject-by-subject basis
    subject_raw_pattern, head_origin_fname, meg_bads_fname, subject_sss_name = \
        format_variable_names(replace_dict, raw_pattern, head_origin_pattern, meg_bad_channel_pattern, sss_pattern)

    raw = preload_raws(subject_paradigm_dir, subject_raw_pattern)
    raw_fname = find_file_matches(subject_paradigm_dir, subject_raw_pattern)[0]

    coords = generate_head_origin(raw.info, subject_paradigm_dir, head_origin_fname) # head origin coordinates
    meg_bads = read_bad_channels_meg_elekta(subject_paradigm_dir, meg_bads_fname) # read marked MEG bad channels
    # maxwell filter the paradigm data
    paradigm_out, paradigm_err = maxwell_filter_paradigm(subject, raw_fname, subject_sss_name, coords, meg_bads)

    if proc_using_erm: # maxwell filter ERM data if specified
        date_paradigm, raw_erm_name, erm_sss_name = handle_erm(raw, subject_erm_dir, erm_pattern) # helper function
        erm_out, erm_err = maxwell_filter_erm(subject, date_paradigm, raw_erm_name, erm_sss_name, meg_bads)
    else:
        continue # no more maxwell filtering needed
