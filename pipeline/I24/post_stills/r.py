# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 11:14:29 2017

@author: web66492
"""

import os
import subprocess

def list_directory(input_path):
    # creates a list everything in a specified directory
    all_in_files = os.listdir(input_path)
    all_in_files.sort()
    return all_in_files

def list_directory_files_of_type(input_path, file_type, starts_with=None):
    # creates a list of all files of a specific type in a specified directory
    all_in_files = list_directory(input_path)
    if starts_with is not None:
        type_files = [fil for fil in all_in_files if fil.endswith(file_type) and fil.startswith(starts_with)]
    else:
        type_files = [fil for fil in all_in_files if fil.endswith(file_type)]
    type_files.sort()
    return type_files

def check_for_dir(dir_path, dir_name, dir_list=None):
    if dir_list is None:
        dir_list = list_directory(dir_path)
    if dir_name not in dir_list:
        mkdir(dir_name)
    return

def mkdir(dir_name, shell_status=True):
    subprocess.call(['mkdir %s' % dir_name], shell=shell_status)
    return

path = '/dls/i24/data/2017/nt14493-63/processing/MR/waylinCD/'
dir_list = list_directory(path)
dose_list = [dose for dose in dir_list if dose.startswith('dose')]
for dose in dose_list:
    dir = path + dose
    mtzs = list_directory_files_of_type(dir, 'mtz', starts_with='PHASER')
    pdbs = list_directory_files_of_type(dir, 'pdb', starts_with='PHASER')
    output_path = path + dose
    output_dir = path + dose + '/refine_auto_3/'
    check_for_dir(output_path, output_dir)
    for pdb, mtz in zip(pdbs,mtzs):
        prefix = 'REFINE_%s'%mtz.split('.')[0]
        print mtz,pdb, prefix
        dir_name = mtz.split('_')[1]+mtz.split('_')[2]
        subprocess.call(['phenix.refine %s/%s %s/%s ordered_solvent=True \
        ordered_solvent.mode=every_macro_cycle ordered_solvent.n_cycles=3 \
        nproc=8 output.prefix=%s gui.base_output_dir=%s \
        refinement.input.xray_data.r_free_flags.generate=True'\
        %(dir,mtz,dir,pdb,prefix,output_dir)], shell=True)
        subprocess.call(['mv REFINE* %s'%output_dir],shell=True)        
