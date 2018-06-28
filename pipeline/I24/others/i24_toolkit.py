# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 09:47:01 2017

@author: web66492
"""

import os
import subprocess
import sys
import time

class file_scripts:
    #general scripts for i24
    #to do: reorganise into separate classes
    def list_directory(self, input_path):
        #creates a list everything in a specified directory
        all_in_files = os.listdir(input_path)
        all_in_files.sort()
        return all_in_files

    def list_directory_files_of_type(self, input_path, file_type, starts_with = None):
        #creates a list of all files of a specific type in a specified directory
        all_in_files = self.list_directory(input_path)
        if starts_with != None:
            type_files = [file for file in all_in_files if file.endswith(file_type) and file.startswith(starts_with)]
        else:
            type_files = [file for file in all_in_files if file.endswith(file_type)]
        type_files.sort()
        return type_files
        
    def to_continue(self, in_val, chck_type):
        #exits script by user input
        if in_val.lower() == 'y' or in_val.lower() == 'yes':
            return
        elif in_val.lower() == 'n' or in_val.lower() == 'no':
            if chck_type == 'prep':
                print('please load modules in the command line i.e. module load global/cluster and module load dials/nightly')
            elif chck_type == 'run':
                print('exiting job submission')
            sys.exit()
        else:
            self.prep_check(chck_type)  
        
    def prep_check(self, check_val):
        #checks to see if user has moded correct linux modules
        if check_val == 'prep':
            prep_val = raw_input("Have you loaded the correct linux modules i.e. for dials and cluster (y/n): ")     
        elif check_val == 'run':
            prep_val = raw_input('Do you wish to continue: (y/n')
        self.to_continue(prep_val, check_val)
        return 
    
    
    def write_process_file(self, process_file_name, process):
        #writes a process.sh file
        p_file_name = "%s.sh"%(process_file_name)
        p_file = open(p_file_name,'w')
        p_file.write('module load dials/nightly \n')
        p_file.write(process)
        p_file.close()
        return p_file_name
        
    def write_new_phil(self, phil_name,new_phil_name,data,run_no,title):
        p_file = open(phil_name,'r')
        new_file = open(new_phil_name, 'w')
        for line in p_file:
            if line.startswith("data ="):
                new_file.write("data = %s\n"%(data))
            elif line.startswith("run_no ="):
                new_file.write("run_no = %s\n"%(run_no))
            elif line.startswith("title ="):
                new_file.write("title = %s ano = true \n"%(title))
            else:
                new_file.write('%s'%(line))
        return
        

class cluster_scripts:
    
    
    def run_cluster_job(self, p_file_name):
        # runs a cluster job with specified parameters
        #to change, default parameters
        subprocess.call(['qsub -cwd -q low.q -pe smp 20 %s'%p_file_name], shell=True)
        return

    def output_cluster_status(self, output_file='out.txt'):
        #outputs cluster job status to a file i.e. out.txt
        subprocess.call(['qstat > %s'%(output_file)], shell= True)        
        return
        
    def check_log(self, iterations = 100, wait_time = 2,output_file='out.txt'
                                                            ,i=0):
        #checks cluster log and waits for it to empty
        i+=1
        self.output_cluster_status(output_file)
        log_file = open(output_file,'r')
        if log_file.readlines() != []:
            if i == iterations:
                print('cannot find blank out.txt')
                sys.exit()
            elif i >= 1:
                print('waiting for queue to empty')
                time.sleep(wait_time)
                self.check_log(iterations = iterations, wait_time = wait_time,
                               output_file=output_file, i=i)
            else:
                self.check_log(iterations = iterations, wait_time = wait_time,
                               output_file=output_file, i=i)
        else:
            return  
            
class command_line_scripts:
    
    def run_command(self, command, shell_status = True):
        subprocess.call([command], shell=shell_status)
        return
    
    def module_load(self, module, shell_status=True):
        subprocess.call(['module load %s'%module], shell=shell_status)
        return
        
    def load_process_modules(self):
        self.module_load('global/cluster')
        self.module_load('dials/nightly')
        return
    
    def mkdir(self, dir_name, shell_status=True):
        subprocess.call(['mkdir %s'%(dir_name)], shell=shell_status)
        return
    
    def check_for_dir(self, dir_path, dir_name, dir_list = None):
        file_runner = file_scripts()        
        if dir_list is None:
            dir_list = file_runner.list_directory(dir_path)
        if dir_name not in dir_list:
            self.mkdir(dir_name)
        return
        
    
    