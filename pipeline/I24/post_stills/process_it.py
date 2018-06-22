import nest
import os
import utils
import snowgoose as sg
import sys
import subprocess
import argparse
###############################
#add global_hawk option to run multiple directorys
########################

def argparser(argv=None):
    parser = argparse.ArgumentParser(description = 'GLOBAL_HAWK\n\
	                                 Automatically run stills_process\
	                                 on a given directory for a specific chip.\n\
	                                 EXAMPLE\n ./global_hawk.py dir=/dls/i24/data/2017/nt14493-63/ \
					 p_name=CuNIR chip_name=waylinCD proctype=auto \n\
	                                 \nFor more information see  DOCUMENT\n https://docs.google.com/document/d/1osARU4TDkosdJZIhcILc7v_foH-4pCearg71k3Nrhg4/edit#heading=h.3n4jjttquv3z')
    parser.add_argument("visit_directory", type=str,
	                    help="set visit directory e.g. /dls/ixx/data/xxxx/nt14493-63")
    parser.add_argument("-ip","--input_path", type=str,
	                    help="set visit directory e.g. /dls/ixx/data/xxxx/nt14493-63")
    parser.add_argument("protein_name", type=str,
			    help="set protein name e.g. CuNIR")
    parser.add_argument("chip_name",type=str,
			    help="set chip name e.g. waylin")
    parser.add_argument("-p","--process_type", type=str,
		    help="set process type", default="bulk", choices=['bulk','auto','manual'])
    parser.add_argument("-o","--output_directory",type=str,
			    help="set output directory name if different from input naming convention")
    parser.add_argument("-j","--job_limit", type=int,
		    help="number of jobs active at same time", default=20)
    parser.add_argument("-i","--iteration_limit", type=int,
			    help="number of log iterations", default=1000)
    parser.add_argument("-w","--wait_time", type=int,
			    help="log wait time before ending cycle", default=10)
    parser.add_argument("-c","--column_numbers", type=int,
			    help="column numbers used if to be stripped from chipname e.g. 1234", default=None)
    parser.add_argument("-s","--step_size", type=int,
			    help="number of images per job", default=200)
    parser.add_argument("-r","--run_number", type=int,
			help="chip run number")
    parser.add_argument("-l","--log_name",type=str,
			    help="name of outputted log file", default='03102017_out.txt')
    parser.add_argument("-a","--auto_run",type=bool, default = False, choices = [True, False],
                            help="if on experiemnt select auto to run skylark job submitter, DOES NOT WORK YET")
    parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2],
	                    help="increase output verbosity")
    args = parser.parse_args()
    return args

def manual_process(cbf_path):
    # potential additions:
    # check to see if stills_process input = experiments.json works
    cbf_path = '/dls/i24/data/2017/nt14493-63/CuNIR/waylinCD/'
    reference_path = '/dls/i24/data/2017/nt14493-63/processing/stills_process/waylinCD/'
    wd = '/dls/i24/data/2017/nt14493-63/processing/scripts/experiment_refinement_process_test_folder/waylinCD/'
    experiments_json_list = nest.find_experiments_json_starts('waylinCD', doses=20, before_limit=5)
    all_out_files = utils.list_directory(wd)
    for file_num in experiments_json_list:
        diff = file_num % 20
        start_num = file_num - diff
        final_num = start_num + 20
        file_num = '%.5d' % file_num
        file_list = ['waylinCD0077_%.5d' % num for num in range(start_num, final_num)]
        ref_exp_json = '%sidx-waylinCD0077_%s_refined_experiments.json' % (
                                    reference_path, file_num)  # idx-waylinCD0077_46664_refined_experiments.json
        print ref_exp_json
        for file in file_list:
            num = file.split('_')[1]
            idx_file = utils.idx_file_check(all_out_files, num)
            if idx_file == []:
                p_file_name = sg.write_manual_process_file(wd, cbf_path, file, ref_exp_json)  # run manual process
                utils.run_cluster_job_with_log(p_file_name)
                utils.check_log(job_lim=20)  # default job limit = 50
                # move_cluster_logs()
                if file == file_list[-1]:
                    break

def auto_process(visit_directory,protein_name,chip_name, chip_run, output_directory, job_lim=20,iteration_lim=1000, wait_time=10, log_name='03102017_out.txt'): #needs checking, auto_process need rewriting
    cbf_path=os.path.join(visit_directory,protein_name,chip_name)
    cbf_list = utils.list_directory_files_of_type(cbf_path,'.cbf')
    wd = os.path.join(visit_directory,'processing/stills_process/',output_directory)
    all_out_files = utils.list_directory(wd)
    list_to_append = []
    print cbf_path, wd
    for file in cbf_list:
        idx_file = utils.idx_file_check(all_out_files, file.split('.')[0])
        if idx_file == []:
            list_to_append.append(file)
            job_length = len(list_to_append)
            if job_length >= 1 or file == cbf_path[-1]:
                print file
                initial_num = list_to_append[0].split('.')[0].split('_')[1]
                final_num = list_to_append[-1].split('.')[0].split('_')[1]
    		if chip_run is None:
    			chip_run = cbf_list[0].split('_')[0] #chipname+run number
   	        else:
			chip_run = "%.4d"%chip_run
                p_file_name = sg.write_multi_stills_file(wd,cbf_path, chip_run, initial_num, final_num)
                list_to_append = []
                utils.check_log(log_file_name='03102017_out.txt', job_lim=20, i=0, iteration_lim=1000, wait_time=10)
                utils.run_cluster_job_with_log(p_file_name)

def bulk_process(visit_directory,protein_name,chip_name, chip_run, output_directory, job_lim=20,step_size=200, column_numbers = None, input_path = None): #needs checking, auto_process need rewriting
    if not input_path:       
        input_path=os.path.join(visit_directory,protein_name,chip_name)
    cbf_list = utils.list_directory_files_of_type(input_path,'.cbf')
    cbf_values = utils.list_cbf_values(input_path,'.cbf')
    output_path = os.path.join(visit_directory,'processing/stills_process/',protein_name,output_directory)
    utils.check_for_dir(os.path.join(visit_directory, 'processing/stills_process'),protein_name)
    utils.check_for_dir(os.path.join(visit_directory,'processing/stills_process',protein_name), output_directory.split('/')[0])
    utils.check_for_dir(os.path.join(visit_directory,'processing/stills_process',protein_name), output_directory)
    initial_num = min(cbf_values)
    final_num = max(cbf_values)
    if column_numbers:
	chip_name = chip_name.strip(str(column_numbers))
    if chip_run is None:
    	chip_run = cbf_list[0].split('_')[0] #chipname+run number
    else:
	chip_run = "%s%.4d"%(chip_name,chip_run)#str(column_numbers),chip_run)#add a %s
    cluster_out=os.path.join(output_path,'sh_outputs')
    utils.check_for_dir(output_path, 'sh_outputs')
    p_file_name=sg.write_array_stills_file(output_path,input_path,chip_name,chip_run,protein_name, visit_directory)
    utils.run_array_job(p_file_name, output_path=cluster_out, initial_num=initial_num,final_num=final_num,step_size=step_size, job_lim=job_lim, nproc=20)

def main(args): 
    if args.output_directory is None:
 	output_dir=args.chip_name
    else:
	output_dir=args.output_directory
    if args.auto_run:
       pass 	
    elif args.process_type == 'manual':
        manual_process(args.visit_directory)
    elif args.process_type == 'auto':
        auto_process(args.visit_directory, args.protein_name, args.chip_name, args.run_no,  output_dir, args.job_limit,args.iteration_limit, args.wait_time, args.log_name)
        subprocess.call([' mv *.sh* /dls/i24/data/2017/nt14493-63/processing/stills_process/%s_processed_jr'%(chip_name)], shell=True)
    elif args.process_type == 'bulk':
	bulk_process(args.visit_directory, args.protein_name, args.chip_name, args.run_number, output_dir, args.job_limit,args.step_size, args.column_numbers, input_path=args.input_path)
       # subprocess.call([' mv *.sh* /dls/i24/data/2017/nt14493-63/processing/stills_process/%s_processed_jr'%(args.chip_name)], shell=True)
    else:
        print(proctype, ' not recognised pleasue use auto or manual as proctype')

if __name__ == '__main__':
    args=argparser()    
    main(args)

        

