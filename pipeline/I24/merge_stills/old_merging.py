# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 09:32:58 2017

@author: web66492
"""
from i24_toolkit import command_line_scripts, file_scripts, cluster_scripts
#from phil_writer import phil_file_writer
import nest1 as nst
import pickle
import sys
import subprocess
import os

def print_flush(string):
    sys.stdout.write('\r%s' %string)
    sys.stdout.flush()

def get_dose(fid, doses=10):
    integer = int(fid.rstrip('.pickle').split('_')[1])
    dose_bin = (integer % doses) + 1
    return dose_bin

def load_modules():
    command_line_runner.module_load('global/cluster')
    command_line_runner.module_load('dials/nightly')
    return

def check_for_dir(dir_path, dir_name, dir_list = None):
    if dir_list is None:
        dir_list = file_runner.list_directory(dir_path)
    if dir_name not in dir_list:
        command_line_runner.mkdir(dir_name)
    return
    
def set_varaibles(merged_dir_path, dose):
    dose_dir_path = '%s/%s'%(merged_dir_path,dose)
    new_phil_file = '%s/%s'%(dose_dir_path, 'CuNIR_prime.phil')
    data = "%s%s"%('/dls/i24/data/2017/nt14493-63/processing/integrated/waylinCD/',dose)
    run_no ="%s%s%s"%('waylin_',dose,'_1.5A')
    title = "%s %s %s"%('waylin',dose,'1.5A')
    process_file_name = '%s/waylinCD_%s'%(dose_dir_path,dose)
    process = "prime.run %s > %s/prime_waylinCD_%s.out"%(new_phil_file,dose_dir_path,dose)
    return dose_dir_path, new_phil_file, data, run_no, title, process_file_name, process
    
def main(*args):
    dir = '/dls/i24/data/2017/nt14493-63/processing/stills_process/'   
    chip_name = 'waylinCD_reprocess'
    doses = 20
    indicator = 'stat_m'
    contiguous_limit = 8

    allowed_keyword_list = ['dir','chip_name','file','indicator','contiguous_limit','before_limit','doses', 'plimits']
    for arg in args:
        k = arg.split("=")[0]
        v = arg.split("=")[1]
        print "Keyword argument: %s=%s" % (k, v)
        there = [True for key in allowed_keyword_list if k in key]
        if True not in there:
            print 'Unknown arg in args:', arg
            print 'Allowed Keywords:', allowed_keyword_list
            print 'Exiting'
            return 0

    indicator_list = ['uc_vol', 'uc_len', 'stat_m', 'd_min', 'size']
    for arg in args:
        k = arg.split("=")[0]
        v = arg.split("=")[1]
        if 'indic' in k:
            if v in indicator_list:
                indicator = v
                print '\n\nYou have chosen to look at:', indicator
            else:
                print 'Unknown Indicator'
                return 0

    dose_dicts = {}
    for i in range(1, doses+1):
        dose_dicts[i] = {}
    for dose in dose_dicts.keys():
        for ind in indicator_list: 
            dose_dicts[dose][ind] = []    
    
    def intFileCheck(all_out_files, cbf_file):
        idx_file = [i for i in all_out_files if i == '%s'%(cbf_file)]
        return idx_file    
    
    merged_dir_path = '%s%s'%(dir,chip_name)
#    all_list = [] # [x for x in range(105000) if x%20]
#    for fid in os.listdir(merged_dir_path):
#        #print fid
#        if fid.startswith('int-0'):
#            integer = int(fid.rstrip('.pickle').split('_')[1])
#            all_list.append(integer)
#        elif fid.startswith('int') and fid.endswith('0.pickle'):
#            integer = int(fid.rstrip('.pickle').split('_')[1])
#            all_list.append(integer)
    starts_list = nst.find_contiguous(chip_name, doses, contiguous_limit, path = dir)
    for c, start_num in enumerate(starts_list[:]):
        s = '%04d:%04d %02d%%  ' % (c, len(starts_list), 100*float(c)/len(starts_list))
        print_flush(s)
        
        for dose_num in range(doses): 
            all_out_files = os.listdir('/dls/i24/data/2017/nt14493-63/processing/scripts/experiment_refinement_process_test_folder/integrated/waylinCD_stills/dose%02d/'%(dose_num))
            fid = 'int-0-waylinCD0077_%05d.pickle' %(start_num + dose_num)
            try:
                jar = pickle.load(open(merged_dir_path+'/'+fid, 'r'))
            except StandardError, e: #includes all intfiles after program breaks....)
                break
            obs = jar['observations'][0]
            uc_len = obs.unit_cell().parameters()[0]
            uc_vol = obs.unit_cell().volume()
            stat_m = obs.statistical_mean()
            d_min = obs.d_min()
            size = obs.size()
            dose_bin = dose_num+1
            dose_dicts[dose_bin]['uc_vol'].append(uc_vol)
            dose_dicts[dose_bin]['uc_len'].append(uc_len)
            dose_dicts[dose_bin]['stat_m'].append(stat_m)
            dose_dicts[dose_bin]['d_min'].append(d_min)
            dose_dicts[dose_bin]['size'].append(size)
            int_file = intFileCheck(all_out_files, fid)
            if int_file == []:
                try:
                    test_jar = pickle.load(open('/dls/i24/data/2017/nt14493-63/processing/scripts/experiment_refinement_process_test_folder/integrated/waylinCD_stills/dose%02d/%s'%(dose_num,fid),'r'))
                except StandardError, e:
                    subprocess.call(['cp %s/%s /dls/i24/data/2017/nt14493-63/processing/scripts/experiment_refinement_process_test_folder/integrated/waylinCD_stills/dose%02d/'%(merged_dir_path,fid,dose_num)], shell=True)
            
            
    for i in range(1, doses+1):
        dose_dir_path = '/dls/i24/data/2017/nt14493-63/processing/scripts/experiment_refinement_process_test_folder/merged/waylinCD_stills/dose%02d'%(i)
        new_phil_file = '%s/%s'%(dose_dir_path, 'CuNIR_prime.phil')
        data = '/dls/i24/data/2017/nt14493-63/processing/scripts/experiment_refinement_process_test_folder/integrated/waylinCD_stills/dose%02d/'%i
        run_no ="%s%s%s"%('waylin_',i,'_reproc_1.5A')
        title = "%s %s %s"%('waylin',i,'_reproc_1.5A')
        process_file_name = '%s/waylinCD_%s'%(dose_dir_path,i)
        process = "prime.run %s > %s/prime_waylinCD_%s.out"%(new_phil_file,dose_dir_path,i)
#        dose_dir_path, new_phil_file, data, run_no, title, process_file_name, process = set_varaibles(merged_dir_path, dose)
#        check_for_dir(dose_dir_path, dose,merged_dir_list)
        file_runner.write_new_phil(original_phil_file, new_phil_file, data, run_no,title)
        file_runner.write_process_file(process_file_name,process)
        cluster.run_cluster_job('%s%s'%(process_file_name,'.sh'))
#        if i%3 == 0:
#            cluster.check_log(iterations = 1000, wait_time = 10,output_file='merging_out.txt')

if __name__ == '__main__':
    command_line_runner = command_line_scripts()
    file_runner = file_scripts()
    load_modules()
    cluster = cluster_scripts()
    original_phil_file = '/dls/i24/data/2017/nt14493-63/processing/merged/waylin/dose1/CuNIR_prime_ref_data.phil'     
    dir_path = '/dls/i24/data/2017/nt14493-63/processing/scripts/experiment_refinement_process_test_folder/'

    dir_name = 'waylinCD'
    main()
