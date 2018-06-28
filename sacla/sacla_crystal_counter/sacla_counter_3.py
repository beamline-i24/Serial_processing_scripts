import re
import subprocess
import sys
import argparse

#----- regex search criteria -----
geometry_file_start=re.compile(r'-----\s*Begin\s*geometry\s*file\s*-----')
geometry_file_end=re.compile(r'-----\s*End\s*geometry\s*file\s*-----')
unit_cell_start=re.compile(r'-----\s*Begin\s*unit\s*cell -----')
unit_cell_end=re.compile(r'-----\s*End\s*unit\s*cell -----')
crystal_start=re.compile(r'---\s*Begin\s*crystal')
crystal_end=re.compile(r'---\s*End\s*crystal')
image_serial = re.compile(r'Image serial number:\s*(\d+)')
indexed_by = re.compile(r'indexed_by =\s*(.*)')
p = re.compile(r'Cell parameters\s*(\d+\.\d+)\s*(\d+\.\d+)\s*(\d+\.\d+)\s*nm,\s*(\d+\.\d+)\s*(\d+\.\d+)\s*(\d+\.\d+)\s*deg')

def argparser(argv=None):
    parser = argparse.ArgumentParser(description = 'Unit Cell Counter\n\
	                                 Creates .dat file contianing the name/path and cctbx data of\
	                                 each int file in a set of directories.\n\
	                                 EXAMPLE\n ./unit_cell_counter.py dir=/dls/i24/data/2017/nt14493-63/ \
					 p_name=CuNIR chip_name=waylinCD proctype=auto\n ')
    parser.add_argument("-i","--input_file", type=str, required=True,
	                    help="input file e.g. /dls/x02-1/data/2017/mx15722-8/processing/acnir/ali/BCQR/BCQR_reindexed.out", default=None)
    parser.add_argument("-o","--output_file", type=str,
	                    help="output file e.g. /dls/x02-1/data/2017/mx15722-8/processing/acnir/ali/BCQR/BCQR_reindexed.out", default='subset.out')
    parser.add_argument("-n","--number_of_crystals", type=int,
		    help="number of crystals in subset", default=1000)
    parser.add_argument("-s","--splitter_size", type=int,
		    help="number of crystals in subset", default=1000)
    parser.add_argument("-sf","--splitter_flag", type=bool, default=False,
		    help="split dataset into subsets of a set size")
    parser.add_argument("-c","--counter", type=bool,
                        help="count number of crystals in file", default=False)
    parser.add_argument("-p","--pacman", type=bool,
                        help="make pacman unit_cell out file", default=False)
    parser.add_argument("-u","--unit_cell_parameter", type=str,
		    help="unit_cell_parameter to plot in pacman", default='a', choices=['a','b','c','al','be','ga'])
    parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2],
	                    help="increase output verbosity")
    args = parser.parse_args()
    return args

def file_len(fname):
    #unused function for potential multiprocessing, finds length of file
    p=subprocess.Popen(['wc', '-l', fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result,err = p.communicate()
    if p.returncode:
       raise IOError(err)
    return int(result.strip().split()[0])

def print_flush(string):
    #Darren Sherrell, prints nicely to screen, good for progress bars etc
    sys.stdout.write('\r%s' % string)
    sys.stdout.flush()

def check_line(line, out_list, counter): 
    #--- search line for crystal, if crystal adds 1 to the total count ---
    #u = image_serial.search(line)
    #if u: print(u.group(1))
    #i = indexed_by.search(line)
    #if i: print(i.group(1))
    cryst_search = crystal_end.search(line)
    if cryst_search:
        counter +=1
    out_list.append(line)
    return out_list, counter

def file_writer(out_list,output_file_name, meta_list=None, pacman=False):
    #--- writes output_files based on input criteria
    print('outputting data')
    with open(output_file_name, 'w') as out_file:
        if pacman:
            for image, cell in out_list:
               out_file.write("%05d   %s \n" %(int(image), str(cell)))
        else:
            if meta_list:
               for item in meta_list:
                   out_file.write("%s" % item)
            for item in out_list:
               out_file.write("%s" % item)

def crystal_counter(args):
    #--- uses regex to count all crystals in .out file
    input_file_name=args.input_file
    out_list = []
    counter = 0
    with open(input_file_name, 'r') as input_file:
        print('seraching for crystals')
        for line in input_file:
            out_list, counter = check_line(line, out_list, counter)
            s = 'number of crystals = %04d' % (counter)
            print_flush(s)
    print('number_of_crystals = %04d'%counter) 

def dataset_splitter(args):
    #splits datasets into subsets of x crystals, total number of  crystals of subsets also specified
    number_of_crystals = args.number_of_crystals
    subset_size = args.splitter_size
    input_file_name=args.input_file
    output_file_name=args.output_file
    counter = 0
    out_list = []
    meta_list = []
    i=0 
    with open(input_file_name, 'r') as input_file:
        print('searching for crystals')
        for line in input_file:
            line_check = line
            meta_list.append(line)
            end = unit_cell_end.search(line_check)
            if end:
               break
        for line in input_file:
            out_list, counter = check_line(line, out_list, counter)
            s = '%04d:%04d %02d%%  ' % (i+counter, number_of_crystals, 100*float(i+counter)/number_of_crystals)
            print_flush(s)
            if  counter == subset_size:
               file_name=str(i)+'-'+str(i+counter)+output_file_name
               file_writer(out_list, file_name, meta_list=meta_list)
               i +=counter
               if i == number_of_crystals:
                  break
               counter = 0
               out_list = []

def pacman(args):
    #produces input files for pacman for plotting unit_cell by image
    number_of_crystals = args.number_of_crystals
    input_file_name=args.input_file
    output_file_name=args.output_file
    params_dict={'a':1,'b':2,'c':3,'al':4,'be':5,'ga':6}
    param=params_dict[args.unit_cell_parameter]
    counter = 0
    out_list = []
    with open(input_file_name, 'r') as input_file:
        print('seraching for crystals')
        for line in input_file:
            s = '%04d:%04d %02d%%  ' % (counter, number_of_crystals, 100*float(counter)/number_of_crystals)
            print_flush(s)
            line_check=line
            u = image_serial.search(line_check)
            if u: 
               image_number = u.group(1)
               continue
            i = indexed_by.search(line_check)
            if i:
               i_check=i.group(1)
               if i_check == 'none-nolatt-nocell':
                  out_list.append([image_number,'None']) 
               continue
            cryst_search = p.search(line_check)
            if cryst_search:
               counter +=1
               cell = float(cryst_search.group(param))*10
               out_list.append([image_number, cell])
            if counter == number_of_crystals:
               break           
    file_writer(out_list, output_file_name, pacman=True)

def main(args):
    #creates a subset of the dataset of x number of crystals
    number_of_crystals = args.number_of_crystals
    input_file_name=args.input_file
    output_file_name=args.output_file
    counter = 0
    out_list = []
    
    with open(input_file_name, 'r') as input_file:
        print('seraching for crystals')
        for line in input_file:
            out_list, counter = check_line(line, out_list, counter)
            s = '%04d:%04d %02d%%  ' % (counter, number_of_crystals, 100*float(counter)/number_of_crystals)
            print_flush(s)
            if counter == number_of_crystals:
               break           
    file_writer(out_list, output_file_name)    

if __name__ == '__main__':
   args=argparser()
   if args.counter:
      crystal_counter(args)
   elif args.pacman:
       pacman(args)
   elif args.splitter_flag:
       dataset_splitter(args)
   else:
       main(args)
