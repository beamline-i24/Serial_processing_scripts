import pickle
import os
import pandas as pd
import sys
import timeit
import argparse
import multiprocessing

def print_flush(string):
    sys.stdout.write('\r%s' % string)
    sys.stdout.flush()

def wrapper(func, *args, **kwargs):
    def wrapped():
	return func(*args, **kwargs)
    return wrapped

def list_ints_from_dir(directory, name):
    path = os.path.join(directory, name)
    try:
	x=os.path.isdir(path)
        if x:
            print "path %s exists"%path
        return [os.path.join(path,int_file) for int_file in os.listdir(path) if int_file.startswith("int")]
    except:
        print "path %s doesn't exist"%(os.path.join(path))
	return []
 
def create_int_list(directory, dir_list):
    #directory = "/dls/i24/data/2018/nt14493-94/processing/stills_process/acnir/battle1234/"
    #dir_list=['dose1','dose2','dose3','dose4','dose5','dose6','dose7','dose8','dose9','dose10']
    dir_list_ints = []
    for name in dir_list:
        listdir = list_ints_from_dir(directory, name) 
        dir_list_ints += listdir
    return dir_list_ints

def grep_column(int_file, df, column): 
    jar = pickle.load(open(int_file, 'r'))
    if column == 'det_dist':
        data=jar['distance']
    else:
        data=jar['observations'][0].unit_cell().parameters()[0]
    df[column][df.index.values == int_file]=data
    return df

def grep_column_mpi(df):
    index_values=df.index.values
    for int_file in index_values:
    	jar = pickle.load(open(int_file, 'r'))
        data=jar['observations'][0].unit_cell().parameters()[0]
        df['cell_type'][df.index.values == int_file]=data
    return df

def create_df_mpi(int_file_list, column='cell_type'):
    value_list = [int_file.split('.')[0].split('/')[-1] for int_file in sorted(int_file_list)]
    coloured_cell_df=pd.DataFrame(index=sorted(int_file_list), columns=[column, 'file_name'])#['det_dist'])#
    coloured_cell_df['file_name']=value_list
    num_processes = multiprocessing.cpu_count()
    chunk_size = int(coloured_cell_df.shape[0]/num_processes)
    chunks = [coloured_cell_df.ix[coloured_cell_df.index[i:i + chunk_size]] for i in range(0, coloured_cell_df.shape[0], chunk_size)] 
    pool = multiprocessing.Pool(processes=num_processes)
    result=pool.map(grep_column_mpi, chunks)
    for i in range(len(result)):
        coloured_cell_df.ix[result[i].index]=result[i] 
    #print(coloured_cell_df)
    return coloured_cell_df

def create_df(int_file_list, column='cell_type'):
    value_list = [int_file.split('.')[0].split('/')[-1] for int_file in sorted(int_file_list)]
    coloured_cell_df=pd.DataFrame(index=sorted(int_file_list), columns=[column, 'file_name'])#['det_dist'])#
    for c, int_file in enumerate(int_file_list[:]):
        s = '%04d:%04d %02d%%  ' % (c, len(int_file_list), 100*float(c)/len(int_file_list))
        print_flush(s)
        coloured_cell_df=grep_column(int_file, coloured_cell_df, column)
    coloured_cell_df['file_name']=value_list
    return coloured_cell_df

def argparser(argv=None):
    parser = argparse.ArgumentParser(description = 'Unit Cell Counter\n\
	                                 Creates .dat file contianing the name/path and cctbx data of\
	                                 each int file in a set of directories.\n\
	                                 EXAMPLE\n ./unit_cell_counter.py dir=/dls/i24/data/2017/nt14493-63/ \
					 p_name=CuNIR chip_name=waylinCD proctype=auto\n ')
    parser.add_argument("-d","--directory", type=str,
	                    help="set visit directory e.g. /dls/ixx/data/xxxx/nt14493-63", default=None)
    parser.add_argument("-D","--directory_list", nargs='+',
		    help="set process type", default=None)
    parser.add_argument("-s","--sub_directory_list",nargs='+',
			    help="give list of ")
    parser.add_argument("-c","--column", type=str,
			    help="cctbx data type to extract i.e. unit cell, detector_distace",
                            choices = ['cell_type','det_dist'], default='cell_type')
    parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2],
	                    help="increase output verbosity")
    args = parser.parse_args()
    if not args.directory and not args.directory_list:
       msg="Unit Cell Counter requires -d directory or -D directory_list to run"
       raise argparse.ArgumentTypeError(msg)
    elif args.directory and args.directory_list:
       msg="-d and -D given. Unit Cell Counter requires -d directory or -D directory_list to run"
       raise argparse.ArgumentTypeError(msg)
    elif args.directory or args.directory_list:
	pass 	
    return args


def main(args):
    column=args.column
    directory=args.directory
    directory_list=args.directory_list
    sub_dir_list=args.sub_directory_list
    if directory_list:
       for directory in directory_list:
           int_file_list = create_int_list(directory, sub_dir_list)
    else:
	int_file_list = create_int_list(directory, sub_dir_list)

    coloured_cell_df = create_df_mpi(int_file_list, column='cell_type')
    coloured_cell_df = coloured_cell_df.set_index('file_name')
    
    print(coloured_cell_df)
    big_ucs=[uc for uc in coloured_cell_df[column] if uc > 97.9 and uc < 98.5]
    small_ucs=[uc for uc in coloured_cell_df[column] if uc > 96.3 and uc < 97]
    other=[uc for uc in coloured_cell_df[column] if uc > 97.6 and uc < 98.0]
    file_dir = directory.split('/')[-1]
    if len(args.sub_directory_list) == 1:
    	coloured_cell_df.to_csv('%s_%s_1.dat'%(sub_dir_list[0],column), sep=' ')
    else:
        coloured_cell_df.to_csv('%s_%s_1.dat'%(file_dir,column), sep=' ')
    
    print("number of big_ucs: ",len(big_ucs), "number of small_ucs: ",len(small_ucs), "number of other ucs: ",len(other)) 

if __name__=='__main__':
   args=argparser()
   main(args)
