import os
import sys
import subprocess
import time


def check_for_dir(dir_path, dir_name, dir_list=None):
    if dir_list is None:
        print 'generating directory list'
        dir_list = list_directory(dir_path)
    joint_path = os.path.join(dir_path,dir_name) 
    if dir_name not in dir_list:
	print 'making folder'
        mkdir(joint_path)
    else:
	print 'directory exists'
    return joint_path

def check_log(log_file_name='03102017_out.txt', job_lim=100, i=0, iteration_lim=1000, wait_time=5):
    i = + 1
    subprocess.call(['qstat > %s' % log_file_name], shell= True)
    count = get_line_count(log_file_name)
    if count > job_lim:
        print("waiting for queue to empty")
        time.sleep(wait_time)
        #add in in_val loop, maybe reset iteration_lim
        if i == iteration_lim:
            in_val = raw_input('Do you wish to continue, queue is taking a while to empty: (y/n')
            if in_val.lower() == 'y' or in_val.lower() == 'yes':
                check_log(log_file_name, job_lim, i, iteration_lim, wait_time)
            elif in_val.lower() == 'n' or in_val.lower() == 'no':
                sys.exit()
    else:
        return


def get_dose(fid, doses=10):
    integer = int(fid.rstrip('.pickle').split('_')[1])
    print integer
    dose_bin = (integer % doses) + 1
    return dose_bin


def get_line_count(filename = 'martin_out.txt'):
    with open(filename, 'r') as my_file:
        count = sum(1 for line in my_file)
    return count

def iter_idx_file_check(dir, cbf_file):
    idx_file = itertools.dropwhile(lambda x: x!='idx-%s_datablock.json'%cbf_file, os.listdir(dir))
    return idx_file

def idx_file_check(all_out_files, cbf_file):
    idx_file = itertools.dropwhile(lambda x: x!='idx-%s_datablock.json'%cbf_file, os.listdir(dir))
    idx_file = [i for i in all_out_files if i == 'idx-%s_datablock.json' % cbf_file]
    return idx_file

def file_check(all_out_files, file_name):
    file = [i for i in all_out_files if i == '%s' % file_name]
    return file

def list_directory(input_path):
    # creates a list everything in a specified directory
    all_in_files = os.listdir(input_path)
    all_in_files.sort()
    return all_in_files

def list_cbf_values(input_path, file_type): 
    all_in_files = list_directory(input_path)
    type_files = [int(fil.split('_')[-1].split('.')[0]) for fil in all_in_files if fil.endswith(file_type)]
    type_files.sort()
    return type_files

def list_directory_files_of_type(input_path, file_type, starts_with=None):
    # creates a list of all files of a specific type in a specified directory
    all_in_files = list_directory(input_path)
    if starts_with is not None:
        type_files = [fil for fil in all_in_files if fil.endswith(file_type) and fil.startswith(starts_with)]
    else:
        type_files = [fil for fil in all_in_files if fil.endswith(file_type)]
    type_files.sort()
    return type_files


def load_process_modules():
    module_load('global/cluster')
    module_load('dials/nightly')
    return


def mkdir(dir_name, shell_status=True):
    subprocess.call(['mkdir %s' % dir_name], shell=shell_status)
    return


def module_load(module_name, shell_status=True):
    subprocess.call(['module load %s' % module_name], shell=shell_status)
    return


def move_cluster_logs(output_path):
    subprocess.call(['mv *.sh.* %s'%output_path], shell=True)
    return


def prep_check(check_val='run'):
    # checks to see if user has loaded correct linux modules
    if check_val == 'prep':
        prep_val = raw_input("Have you loaded the correct linux modules i.e. for dials and cluster (y/n): ")
    else:
        prep_val = raw_input('Do you wish to continue: (y/n')
    to_continue(prep_val, check_val)
    return


def print_flush(string):
    sys.stdout.write('\r%s' % string)
    sys.stdout.flush()


def output_cluster_status(output_file='out.txt'):
    # outputs cluster job status to a file i.e. out.txt
    subprocess.call(['qstat > %s' % output_file], shell=True)
    return


def run_array_job(p_file_name, output_path='.',  initial_num=1, final_num=64000, step_size=200, job_lim=20, nproc=20): 
   if int(initial_num) == 0:
	initial_num=1
   subprocess.call(['qsub -cwd -q low.q -o {6} -e {6}  -pe smp {0} -t {1}-{2}:{3} -tc {4} {5}'.format(nproc, initial_num, final_num, step_size, job_lim,p_file_name, output_path)], shell=True)
   return

def run_cluster_job(p_file_name):
    # runs a cluster job with specified parameters
    # to change, default parameters
    subprocess.call(['qsub -cwd -q low.q -pe smp 20 %s' % p_file_name], shell=True)
    return


def run_cluster_job_with_output_path(p_file_name, output_path):
    # runs a cluster job with specified parameters
    # to change, default parameters
    subprocess.call(['qsub -cwd -q low.q -o {0} -e {0} -pe smp 20 {1}'.format(output_path,  p_file_name)], shell=True)
    return

def run_cluster_job_with_log(p_file_name, log_file_name='martin_out.txt'):
    subprocess.call(['qsub -cwd -q low.q -pe smp 20 %s' % p_file_name], shell=True)
    subprocess.call(['qstat > %s'%log_file_name], shell=True)
    return


def run_command(command, shell_status=True):
    subprocess.call([command], shell=shell_status)
    return


def to_continue(in_val, check_type):
    # exits script by user input
    if in_val.lower() == 'y' or in_val.lower() == 'yes':
        return
    elif in_val.lower() == 'n' or in_val.lower() == 'no':
        if check_type == 'prep':
            print('please load modules in the command line i.e. module load global/cluster and module load dials/'
                  'nightly')
        elif check_type == 'run':
            print('exiting job submission')
        sys.exit()
    else:
        prep_check(check_type)
        
        
def write_new_prime_phil(phil_name,new_phil_name,data,run_no,title):
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



