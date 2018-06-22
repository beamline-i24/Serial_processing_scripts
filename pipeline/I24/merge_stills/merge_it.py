#!/dls_sw/apps/python/anaconda/1.7.0/64/bin/python
"""
Designed to Merge intergrated files

Created on 31 Oct 2017
@author: web66492 Martin Appleby
helper: voe31998 Darren Sherrell
"""

import utils
#from phil_writer import phil_file_writer
import nest as nst
import pickle
import sys
import subprocess
import os

def argparser(argv=None):
    parser = argparse.ArgumentParser(description = 'PUSHPAK\n\
	                                 Merges Integrated stills data using Prime\n\
	                                 EXAMPLE\n ./global_hawk.py dir=/dls/i24/data/2017/nt14493-63/ \
					 p_name=CuNIR chip_name=waylinCD proctype=auto \n\
	                                 \nFor more information see  DOCUMENT\n https://docs.google.com/document/d/1osARU4TDkosdJZIhcILc7v_foH-4pCearg71k3Nrhg4/edit#heading=h.3n4jjttquv3z')
    parser.add_argument("input_directory", type=str,
	                    help="set inout directory e.g. /dls/ixx/data/xxxx/nt14493-63/processing/stills_process/")
    parser.add_argument("chip_name",type=str,
			    help="set chip name e.g. waylin")
    parser.add_argument("-p","protein_name", type=str,
			    help="set protein name e.g. CuNIR")
    parser.add_argument("-o","--output_directory",type=str,
			    help="set output directory name if different from input naming convention")
    parser.add_argument("-d","--doses", type=int,
		    help="number of doses used in experiment", default=10)
    parser.add_argument("-e","--experiment_type", type=str,
			    help="type of expeirmental data being analysed, stills is a standard experiment,\
				  doses sorts the integrated files by dose first, contiguous only \
				  merges doses that have a certain number of consecutive hits", default='stills'\
			    choices = ['stills', 'doses', 'contiguous'])
    parser.add_argument("-c","--contiguous_limit", type=int,
			    help="number of consecutive hits for int files to be included in merge", default=10)
    parser.add_argument("-j","--job_limit", type=int,
		    help="number of jobs active at same time", default=20)
    parser.add_argument("-i","--iteration_limit", type=int,
			    help="number of log iterations", default=1000)
    parser.add_argument("-w","--wait_time", type=int,
			    help="log wait time before ending cycle", default=10)
    parser.add_argument("-s","--step_size", type=int,
			    help="number of images per job", default=200)
    parser.add_argument("-r","--run_number", type=int,
			help="chip run number")
    parser.add_argument("-l","--log_name",type=str,
			    help="name of outputted log file", default='03102017_out.txt')
    parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2],
	                    help="increase output verbosity")
    args = parser.parse_args()
    return args

def write_process_file(process_file_name, process):
    #writes a process.sh file
    p_file_name = "%s.sh"%(process_file_name)
    p_file = open(p_file_name,'w')
    p_file.write('module load dials/nightly \n')
    p_file.write(process)
    p_file.close()
    return p_file_name

def write_new_phil(phil_name, new_phil_name, data,run_no, title):
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

def set_variables(out_dir, dose, chip_name):
    dose_dir_path = os.path.join(out_dir,'test','merged','dose%02d'%(dose))
    utils.check_for_dir(os.path.join(out_dir,'test','merged'),'dose%02d'%(dose))
    new_phil_file = os.path.join(dose_dir_path, 'CuNIR_prime.phil')
    data_path = os.path.join(out_dir,'test','dose%02d'%dose)
    run_no ="%s%s%s"%('waylin_',dose,'_reproc_1.5A_10000')
    title = "%s %s %s"%('waylin',dose,'reproc_1.5A_10000')
    process_file_name = '%s/waylin_%s'%(dose_dir_path,dose)
    process = "prime.run %s > %s/prime_waylin_%s.out"%(new_phil_file,dose_dir_path,dose)
    return dose_dir_path, new_phil_file, data_path, run_no, title, process_file_name, process

def dose_merge(input_directory, chip_name, protein_name, run_number, doses, output_directory, job_limit, iteration_limit, wait_time):
    stills_dir_path = os.path.join(input_directory, chip_name)
    print stills_dir_path
    #starts_list = nst.find_contiguous(chip_name, doses, contiguous_limit, path = dir)
    int_list=nst.list_searcher(stills_dir_path, wild='int-0')
    for c, num in enumerate(int_list[:]):
        s = '%04d:%04d %02d%%  ' % (c, len(int_list), 100*float(c)/len(int_list))
        utils.print_flush(s)
        fid = 'int-0-%s%04d_%05d.pickle' %(chip_name, run_number, num)
	print fid
        dose_num = utils.get_dose(fid, doses)
	print doses,num, dose_num
        try:
            os.listdir(os.path.join(output_directory,'integrated', protein_name, chip_name))
        else:
            utils.mkdir(os.path.join(output_directory,'integrated', protein_name, chip_name))
	utils.check_for_dir(os.path.join(output_directory,'integrated', protein_name, chip_name),'dose%02d'%dose_num)
        out_path = os.path.join(output_directory,'dose%02d'%dose_num)
	all_out_files = os.listdir(out_path)
	try:
            print 'searching for int pickle in input directory'
            jar = pickle.load(open(os.path.join(stills_dir_path,fid), 'r'))
        except StandardError, e: #includes all intfiles after program breaks....)
            print "couldnt load int pickle"
	    continue
        try:
            print 'searching for int pickle in output folder'
            test_jar = pickle.load(open(os.path.join(out_path,fid),'r'))
	    print 'found int pickle in output folder'
        except StandardError, e:
	    print 'couldnt find int pickle in output folder, copying file'
            subprocess.Popen(['cp','%s %s'%(os.path.join(stills_dir_path,fid),out_path)],stderr=subprocess.PIPE)
	    continue
    #'merged',args.protein_name, args.chip_name
    utils.check_for_dir(input_directory,'merged')
    for i in range(1, doses+1):
	print 'dose'+ str(i)
        dose_dir_path, new_phil_file, data_path, run_no, title, process_file_name, process = set_variables(out_dir,i)
	write_new_phil(original_phil_file, new_phil_file, data_path, run_no,title)
        write_process_file(process_file_name,process)
        utils.run_cluster_job('%s%s'%(process_file_name,'.sh'))
        if i%3 == 0:
            utils.check_log(iteration_lim = 1000, wait_time = 10,log_file_name='merging_out.txt')
    pass

def stills_merge(input_directory, chip_name, protein_name, run_number, output_directory, job_limit, iteration_limit, wait_time):
    dose_dir_path, new_phil_file, data_path, run_no, title, process_file_name, process = set_variables(out_dir,i)
    write_new_phil(original_phil_file, new_phil_file, data_path, run_no,title)
    write_process_file(process_file_name,process)
    utils.run_cluster_job('%s%s'%(process_file_name,'.sh'))
    pass

def contiguous_merge():
    doses=args.doses
    contiguous_limit = args.contiguous_limit
    chip_name = args.chip_name

    merged_dir_path = os.path.join(dir, chip_name)
    print merged_dir_path
    #starts_list = nst.find_contiguous(chip_name, doses, contiguous_limit, path = dir)
    int_list=nst.list_searcher(merged_dir_path, wild='int-0')
    utils.check_for_dir(out_dir,'test')
    for c, num in enumerate(int_list[10000:10001]):
        s = '%04d:%04d %02d%%  ' % (c, len(int_list), 100*float(c)/len(int_list))
        utils.print_flush(s)
        fid = 'int-0-waylinEF0079_%05d.pickle' %(num)
	print fid
        dose_num = utils.get_dose(fid, doses)
	print doses,num, dose_num
	utils.check_for_dir(os.path.join(out_dir,'test'),'dose%02d'%dose_num)
        out_path = os.path.join(out_dir,'test','dose%02d'%dose_num)
	all_out_files = os.listdir(out_path)
	try:
            print 'searching for int pickle in input directory'
            jar = pickle.load(open(os.path.join(merged_dir_path,fid), 'r'))
        except StandardError, e: #includes all intfiles after program breaks....)
            print "couldnt load int pickle"
	    continue
        try:
            print 'searching for int pickle in output folder'
            test_jar = pickle.load(open(os.path.join(out_path,fid),'r'))
	    print 'found int pickle in output folder'
        except StandardError, e:
	    print 'couldnt find int pickle in output folder, copying file'
            subprocess.Popen(['cp','%s %s'%(os.path.join(merged_dir_path,fid),out_path)],stderr=subprocess.PIPE)
	    continue

    utils.check_for_dir(dir,'merged')
    for i in range(1, doses+1):
	print 'dose'+ str(i)
        dose_dir_path, new_phil_file, data_path, run_no, title, process_file_name, process = set_variables(out_dir,i)
	write_new_phil(original_phil_file, new_phil_file, data_path, run_no,title)
        write_process_file(process_file_name,process)
        utils.run_cluster_job('%s%s'%(process_file_name,'.sh'))
        if i%3 == 0:
            utils.check_log(iteration_lim = 1000, wait_time = 10,log_file_name='merging_out.txt')
    pass

def main(args):
    if args.output_directory is not None:
	    output_directory = args.output_directory 
    else:	
    	output_directory = os.path.join(args.input_directory)
        try: 
	    os.listdir(output_directory)
        except:
            utils.mkdir(output_directory)
    if args.experiment_type == 'stills':
	stills_merge(args.input_directory, args.chip_name, args.protein_name, args.run_number, output_directory, args.job_limit, args.iteration_limit, args.wait_time)
    elif args.experiment_type == 'doses':
	doses_merge(args.input_directory, args.chip_name, args.protein_name, args.run_number, args.doses, output_directory, args.job_limit, args.iteration_limit, args.wait_time)
    elif args.experiment_type == 'contiguous':
        contiguous_merge()
    else:
        print('experiment type not recognised: ' + str(args.experiment_type)
   
if __name__ == '__main__':
    utils.load_process_modules()
    original_phil_file = '/dls/i24/data/2017/nt14493-63/processing/merged/waylin/dose1/CuNIR_prime_ref_data.phil'
    dir_path = '/dls/i24/data/2017/nt14493-63/processing/scripts/experiment_refinement_process_test_folder/'

    dir_name = 'waylinCD'
    args=argparser()
    main(args)
