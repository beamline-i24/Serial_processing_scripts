# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 00:13:45 2017

@author: web66492
"""
import snowgoose as sg
import subprocess
import pickle
import sys, sched, time
import os
import random as rand
import utils
import global_hawk

""" TO DO LIST
1a. check v2 and assimilate good changes
1.Tidy up/fully automate for easy command line running.
2. collect together with other fleetwing programs
2aa. spy_snail, sloth and other similar programs neeed to be converted also i.e. write_file_from_directory.py
2a. make sure global_hawk and skylark do different things
2b. fleetwing gui....?
3. sort out process.phil automation (feed in or selection)
4. make a gui incorporating sloth and skylark
5. interactive mode - add/pick own jobs/change job priority (job submitting api...?)
    select images to skip that is 'wrong'
"""

def phil_file_checker(p_name):
    if p_name.lower() == 'hewl':    
        process_phil_path = '/dls/i24/data/2017/nt14493-78/processing/stills_process/hewl_process.phil'
    elif p_name.lower() == 'dtpa':
        process_phil_path = '/dls/i24/data/2017/nt14493-78/processing/stills_process/dtpa_process.phil'
    elif p_name.lower() == 'cunir':
        process_phil_path = '/dls/i24/data/2017/nt14493-78/processing/stills_process/cunir_process.phil'
    elif p_name.lower() == 'laccase':
        process_phil_path = '/dls/i24/data/2017/nt14493-78/processing/stills_process/laccase_process.phil'
    elif p_name.lower() == 'tvnir':
        process_phil_path = '/dls/i24/data/2017/nt14493-78/processing/stills_process/tvnir_process.phil'
    elif p_name.lower() == 'dhp':
        process_phil_path = '/dls/i24/data/2017/nt14493-78/processing/stills_process/dhp_process.phil' 
    elif p_name.lower() == 'cytcp':
        process_phil_path = '/dls/i24/data/2017/nt14493-78/processing/stills_process/cytcp_process.phil'
    elif p_name.lower() == 'nod':
        process_phil_path = '/dls/i24/data/2017/nt14493-78/processing/stills_process/nod_process.phil'
    else:
        process_phil_path = '/dls/i24/data/2017/nt14493-78/processing/stills_process/dtpa_process.phil'
    return process_phil_path

def write_process_file(input_path, firstnum, lastnum, c_name,c_dir_name, run_no, p_name):
    dials = 'dials.stills_process'
    print p_name, c_dir_name
    output_location = '/dls/i24/data/2017/nt14493-78/processing/process_stills_2/%s/%s/'%(p_name,c_dir_name)
    input_file = '%s%s%s_{%s..%s}.cbf'% (input_path,c_name,run_no,firstnum,lastnum)
    #    if p_name == 'adc':
    #        process_phil_path = '/dls/i24/data/2017/nt14493-78/processing/new_process.phil'#process_phil_path = '/dls/i24/data/2017/nt14493-65/processing/process_' + p_name +'.phil'
    if p_name.lower() == 'hewl':    
        process_phil_path = '/dls/i24/data/2017/nt14493-78/processing/stills_process/hewl_process.phil'
    elif p_name.lower() == 'dtpa':
        process_phil_path = '/dls/i24/data/2017/nt14493-78/processing/stills_process/dtpa_process.phil'
    elif p_name.lower() == 'cunir':
        process_phil_path = '/dls/i24/data/2017/nt14493-78/processing/stills_process/cunir_process.phil'
    elif p_name.lower() == 'laccase':
        process_phil_path = '/dls/i24/data/2017/nt14493-78/processing/stills_process/laccase_process.phil'
    elif p_name.lower() == 'tvnir':
        process_phil_path = '/dls/i24/data/2017/nt14493-78/processing/stills_process/tvnir_process.phil'
    elif p_name.lower() == 'dhp':
        process_phil_path = '/dls/i24/data/2017/nt14493-78/processing/stills_process/dhp_process.phil'
    elif p_name.lower() == 'cytcp':
        process_phil_path = '/dls/i24/data/2017/nt14493-78/processing/stills_process/cytcp_process.phil'
    elif p_name.lower() == 'nod':
        process_phil_path = '/dls/i24/data/2017/nt14493-78/processing/stills_process/nod_process.phil'
    else:
        process_phil_path = '/dls/i24/data/2017/nt14493-78/processing/stills_process/dtpa_process.phil'
    dials_args = '%s %s %s-%s%s'%(process_phil_path,'mp.nproc=20 >',firstnum,lastnum,'_stills_proc.out')
    process = '%s %s %s'% (dials, input_file, dials_args)    
    p_file_name = "%s%s-%s-%s_process.sh"%(output_location,c_name,firstnum,lastnum)
    p_file = open(p_file_name,'w')
    p_file.write('#!/bin/sh\n')
    p_file.write('cd %s'%(output_location))
    p_file.write('\n module load dials/nightly \n')
    p_file.write(process)
    p_file.close()
    print(p_file_name, process)
    return p_file_name  

    
def checkDir(p_name, c_dir_name):
    protein_out_path = '/dls/i24/data/2017/nt14493-78/processing/process_stills_2/'+p_name
    if os.path.exists(protein_out_path) != True:
            subprocess.call(['mkdir %s'%(protein_out_path)], shell=True)
    chip_out_path = protein_out_path + '/' + c_dir_name
    if os.path.exists(chip_out_path) != True:
            subprocess.call(['mkdir %s'%(chip_out_path)], shell=True)
            
            
def getDirListFromPickle(path):
    num_per_file_dict = pickle.load(open(path,'r'))
    dir_paths_list = num_per_file_dict.keys()
    dir_paths_list.sort() 
    return dir_paths_list

def pathInitialiser(path):
    print(path)
    p_name = path.split('/')[-3]
    c_dir_name = path.split('/')[-2]
    checkDir(p_name, c_dir_name)
    dir_contents_list = [file for file in os.listdir(path) if file.endswith('.cbf')]
    dir_contents_list.sort()
    idx_path = '/dls/i24/data/2017/nt14493-78/processing/process_stills_2/'+ p_name +'/' + c_dir_name 
    idx_list = os.listdir(idx_path)
    return p_name, c_dir_name,dir_contents_list,idx_list
    
def getChipName(string):
    name = (string.split('.'))[0]
    c_name = (string.split('_'))[0][:-4]
    return name, c_name

def getRunNum(string, list_to_append):
    run_no = (string.split('_'))[0][-4:]
    firstnum = ((list_to_append[0].split('_'))[1].split('.'))[0]
#    lastnum =int(firstnum)+100
    lastnum = ((list_to_append[-1].split('_'))[1].split('.'))[0]
    job_length = int(lastnum) - int(firstnum)
    return run_no, firstnum, lastnum, job_length

def jobSubmitter(sc,path):
    pickle_path = 'num_per_file_dict.pickle'
    """list of directories
    that have had file changes produced by spysnail
    May be worth trying to combine into one document                                                
    """
    #    path = '/dls/i24/data/2017/nt14493-78/'
    #    dir_paths_list = os.listdir(path)
    #    dir_paths_list = [path + dir for dir in dir_paths_list]
    #dir_paths_list.remove('/dls/i24/data/2017/nt14493-65/adc/adrian78')
    #    print(dir_paths_list)
    #dir_paths_list.append('/dls/i24/data/2017/nt14493-65/hewl/briony')
    #dir_paths_list.append('/dls/i24/data/2017/nt14493-65/hewl/carter')
    dir_paths_list = getDirListFromPickle(pickle_path)
    #dir_paths_list.reverse()
    for path in dir_paths_list:
        p_name, c_dir_name,dir_contents_list,idx_list = pathInitialiser(path)
        list_to_append = []
        i=0
        for file in dir_contents_list:
                name, c_name = getChipName(file)
                idx_file = utils.idx_file_check(idx_list, name)
                if idx_file == []:
                    print(name)
                    list_to_append.append(file)
                    run_no, firstnum, lastnum, job_length = getRunNum(file, list_to_append)
                    if job_length >= 100 or file == dir_contents_list[-1]:
                        i+=100
                        p_file_name = write_process_file(path, firstnum, lastnum, c_name, c_dir_name, run_no, p_name)
                        list_to_append = []
                        utils.check_log()  
                        utils.run_cluster_job(p_file_name)
                        if i >= 400:
                            break
                            
       global_hawk.bulk_process()
      
s = sched.scheduler(time.time, time.sleep)
def main(*args):
    args_dict = {}
    allowed_keyword_list = ['path']
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
        else:
            args_dict[k] = v
    
    path = args_dict['path']
    try:
        while True:
            s.enter(10, 60, jobSubmitter, (s,path))
            s.run()
    except KeyboardInterrupt:
        return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print '\n\t\t\t\tSKYLARK'
        print "\t\t\t\tYou Must Run Spy_snail First \n"
        print "\t\t\t\tSkylark runs a scheduler which reads from a directory list\
        from a pickele file then submits processing jobs to the cluster.\n"
        print "\t\t\t\tEXAMPLE\n ./skylark.py path=/dls/i24/data/2017/nt14493-78/ \n"
        print '\t\t\t\tDOCUMENT\n https://docs.google.com/document/d/1osARU4TDkosdJZIhcILc7v_foH-4pCearg71k3Nrhg4/edit#heading=h.3n4jjttquv3z \n\n'
    else:
         utils.load_process_modules()
         print 'check cluster has loaded correctly'
         x = main(*sys.argv[1:])
         print x
         
""" GLOBAL_HAWK and SKYLARK run the same (small differences) job submission script
    GLobal_Hawl runs for an individual set chip directory whilst skylark runs for all 
    chip directories in a isit that have changes being made to them
"""
