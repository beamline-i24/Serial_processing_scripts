# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 14:47:01 2017

@author: web66492
"""
import os

def write_array_stills_file(output_path,input_path, c_name, run_no, p_name, visit_directory):
    dials = 'dials.stills_process'
    input_file = '$(eval echo "%s%s_1_{$i..$f}.cbf")' % (input_path, run_no)
    process_phil_path = os.path.join(visit_directory, 'processing/stills_process', p_name +'.phil')
    dials_args = '%s mp.nproc=20 > $i-$f.out' % (process_phil_path)
    process = '%s %s %s' % (dials, input_file, dials_args)
    p_file_name = "process.sh" 
    p_file = open(os.path.join(output_path,p_file_name), 'w')
    p_file.write('#!/bin/sh\n')
    p_file.write('module load dials \n')
    p_file.write('initial_num=$((SGE_TASK_ID))\n')
    p_file.write('printf -v i "%04d" $initial_num \n')
    p_file.write('final_num=$((initial_num+SGE_TASK_STEPSIZE)) \n')
    p_file.write('printf -v f "%04d" $final_num \n')
    p_file.write('echo $initial_num $final_num $i $f > out.txt \n')
    p_file.write('cd %s \n' % output_path)
    p_file.write(process)
    p_file.close()
    print(os.path.join(output_path,p_file_name), process)
    return os.path.join(output_path,p_file_name)


def write_single_stills_file(dir_path, filename):#input_path, firstnum, lastnum, c_name,c_dir_name, run_no, p_name):
    dials = 'dials.stills_process'
    input_file = '%s.cbf'% (filename)
    process_phil_path = '/dls/i24/data/2017/nt14493-63/processing/stills_process/waylinCD/process.phil'#process_phil_path = '/dls/i24/data/2017/nt14493-65/processing/process_' + p_name +'.phil'
    dials_args = '%s %s %s%s'%(process_phil_path,'mp.nproc=20 >',filename,'_stills_proc.out')
    process = '%s %s %s'% (dials, input_file, dials_args)
    p_file_name = "%s_process.sh"%(filename)
    p_file = open(p_file_name,'w')
    p_file.write('#!/bin/sh\nmodule load dials/nightly\n')
    p_file.write('cd ' + dir_path +' \n')
    p_file.write(process)
    p_file.close()
    print(p_file_name)
    return p_file_name


def write_multi_stills_file(output_location,cbf_path, chip_run, intial_num, final_num):#input_path, firstnum, lastnum, c_name,c_dir_name, run_no, p_name):
    dials = 'dials.stills_process'
    input_file = '{%s..%s}'% (intial_num, final_num)
    namer = '%s_%s-%s'%(chip_run,intial_num,final_num)
    print namer
    output_path = output_location
    process_phil_path = '/dls/i24/data/2017/nt14493-63/processing/stills_process/waylinAB_jr/waylinAB_process.phil'#process_phil_path = '/dls/i24/data/2017/nt14493-65/processing/process_' + p_name +'.phil'
    dials_args = '%s %s %s%s'%(process_phil_path,'mp.nproc=20 >', namer, '_stills_proc.out')
    process = '%s %s/%s_%s.cbf %s' % (dials,cbf_path,chip_run,input_file, dials_args)
    p_file_name = "%s_process.sh" % namer
    p_file = open(p_file_name, 'w')
    p_file.write('#!/bin/sh\nmodule load dials/nightly\n')
    p_file.write('cd ' + output_path + ' \n')
    p_file.write(process)
    p_file.close()
    print(p_file_name)
    return p_file_name


def write_manual_process_file(output_dir, cbf_dir, filename, ref_exp_json = None):
    #ref_exp_json is the exp_json file produced for an image in 0-5 that can be indexed and then used to give set orientations etc to future processes
    #potential chages:
        #change log names?
        #change the .phils to better settings
    #working directory path - where to spit out outputs
    #.cbf_file without .cbf
    datablock = '%s_datablock.json'%(filename) #the outputted datablock file from dials import
    imprt = 'dials.import %s%s.cbf output.datablock=%s \n'%(cbf_dir,filename, datablock) # create datablock.json
    fnd_spt_phil = output_dir+'spotfind.phil' #dials find_spots parameters, currently using defaults
    strng_pckl = '%s_strong.pickle'%(filename) #the outputted strong.pickle file from find spots
    fnd_spts = 'dials.find_spots %s output.reflections=%s %s \n'%(datablock, strng_pckl, fnd_spt_phil) #create strong.pickle
    idx_phil = output_dir+'index.phil' #dials index paramters, currently using defaults
    idx_pckl = 'idx-%s_indexed.pickle'%(filename) #outputted indexed.pickle
    exp_json = 'idx-%s_experiments.json'%(filename) #outputted experiments.json
    # check for reference experiments json
    if ref_exp_json is not None:
        indx = 'dials.index %s %s %s output.experiments=%s output.reflections=%s %s \n'%(
                            datablock, strng_pckl, ref_exp_json, exp_json, idx_pckl, idx_phil) # create img experiments json and indexed.pickle
    else:
        indx = 'dials.index %s %s output.experiments=%s output.reflections=%s %s \n'%(datablock, strng_pckl, exp_json, idx_pckl, idx_phil) # create img experiments json and indexed.pickle
    int_phil = output_dir+'integrate.phil' #dials integrate paramters, currently using defaults
    int_pckl = 'idx-%s_integrated.pickle'%(filename) #outputted intergrated.pickle
    int_exp_json = 'idx-%s_integrated_experiments.json'%(filename) #outputted integrated experiments json
    #create intergrated.pickle and intergrated_experiments.json
    intgrt = 'dials.integrate %s %s output.experiments=%s output.reflections=%s %s \n'%(exp_json, idx_pckl, int_exp_json, int_pckl,int_phil)
    frm_extr_pckl = 'int-%s.pickle'%(filename) #int file
    #create int files
    frm_extr = 'cxi.frame_extractor input.experiments=%s input.reflections=%s output.filename=%s \n'%(int_exp_json, int_pckl, frm_extr_pckl)
    #write process file for image
    p_file_name = "%s_manual_process.sh"%(filename)
    p_file = open(p_file_name,'w')
    p_file.write('#!/bin/sh\n')
    p_file.write('cd %s'%(output_dir))
    p_file.write('\n source /dls_sw/apps/dials/custom/dev-1102/dials-dev-1102/dials_env.sh \n')
    p_file.write(imprt)
    p_file.write(fnd_spts)
    p_file.write(indx)
    p_file.write(intgrt)
    p_file.write(frm_extr)
    p_file.close()
    print p_file_name
    return p_file_name


def write_process_file(input_path, firstnum, lastnum, c_name, c_dir_name, run_no, p_name):
    dials = 'dials.stills_process'
    print p_name, c_dir_name
    output_location = '/dls/i24/data/2017/nt14493-65/processing/stills_process/%s/%s/' % (p_name, c_dir_name)
    input_file = '%s/%s%s_{%s..%s}.cbf' % (input_path, c_name, run_no, firstnum, lastnum)
    if p_name == 'adc':
        process_phil_path = '/dls/i24/data/2017/nt14493-65/processing/new_process.phil'  # process_phil_path = '/dls/i24/data/2017/nt14493-65/processing/process_' + p_name +'.phil'
    else:
        process_phil_path = '/dls/i24/data/2017/nt14493-65/processing/danny/lyso_process.phil'
    dials_args = '%s %s %s-%s%s' % (process_phil_path, 'mp.nproc=20 >', firstnum, lastnum, '_stills_proc.out')
    process = '%s %s %s' % (dials, input_file, dials_args)
    p_file_name = "%s%s-%s-%s_process.sh" % (output_location, c_name, firstnum, lastnum)
    p_file = open(p_file_name, 'w')
    p_file.write('#!/bin/sh\n')
    p_file.write('cd %s' % output_location)
    p_file.write('\n module load dials/nightly \n')
    p_file.write(process)
    p_file.close()
    print(p_file_name, process)
    return p_file_name
