#MODULES
import os
import numpy as np
import pandas as pd
import argparse
import pickle 
import sys
import multiprocessing
 
def argarser():
    parser = argparse.ArgumentParser( description="blah")
    parser.add_argument( "-l", "--input_list",
                        help="if you use this flag you must have a input list file" )
    parser.add_argument( "-i", "--no_of_images", type=int,
                        help="if you want to select a random sample of of images give number" )
    parser.add_argument( "-s", "--stills_directory", type=str,
                        help="stills processing directory" )
    parser.add_argument("-d", "--dose", type=int,
                        help="dose number in a dose experiment")
    parser.add_argument("-td", "--total_dose", type=int,
                        help="number of doses")
    parser.add_argument("-uc", "--unit_cell", type=bool,
                        help="filter ints by unit cell cutoff")
    parser.add_argument("-ucc", "--unit_cell_cutoff", type=int,
                        help="upper/lower limit of unit_cell polymorphs", default=97.2)
    parser.add_argument("-uct", "--unit_cell_target", type=str,
                        help="flag unit_cell as bigger or smaller than target, default big", default='Big', choices=['Big', 'Small'])
    args=parser.parse_args()
    if args.input_list and args.stills_directory:
       parser.error("cannot have two inputs -l and -s")
    elif args.input_list or args.stills_directory:
       pass
    else:
       parser.error("must have an input: -l or -s")
    if args.dose and args.total_dose:
       pass
    elif args.dose or args.total_dose:
       parser.error("-d and -td are both needed")
    return args
 
def print_flush(string):
    sys.stdout.write('\r%s' % string)
    sys.stdout.flush()

def get_int_pickles( still_dir , dose=None, doses=None):
    # create empty np array for int+pwds
    pickle_list = np.array( [ [ ] ] )
    # finds all pwd and files in the still dir
    for path, dirs, files in os.walk( still_dir ):
        for name in files:
            # searches for int files
            if name.startswith( "int" ) and name.endswith( ".pickle" ):
                if dose:# creates complete int.pickle path
                    integer = int(name.rstrip('.pickle').split('_')[1])
                    if (integer%doses) +1 == dose:
                    	pickle_pwd = os.path.join( path, name )
                    	# inputs pickle_pwd into np array
                    	pickle_list_1 = np.array( [ [ pickle_pwd ] ] )
                    	pickle_list = np.concatenate( ( pickle_list, pickle_list_1 ), axis=1 )
                else:
                    pickle_pwd = os.path.join( path, name )
                    # inputs pickle_pwd into np array
                    pickle_list_1 = np.array( [ [ pickle_pwd ] ] )
                    pickle_list = np.concatenate( ( pickle_list, pickle_list_1 ), axis=1 )
    # returns single column np array of int_pwds
    return pickle_list

def get_int_pickles_uc( still_dir, unit_cell_cutoff=97.2, unit_cell_target='Big', dose=None, doses = None): 
    # create empty np array for int+pwds
    pickle_list = np.array( [ [ ] ] )
    # finds all pwd and files in the still dir
    print still_dir
    files=os.listdir(still_dir)
    length=float(len(files))
    for c, name in enumerate(files):
            # searches for int files
            s = '%04d:%04d %02d%%  ' % (c, length, 100*c/length)
            print_flush(s)
            if name.startswith( "int" ) and name.endswith( ".pickle" ):
                if dose:# creates complete int.pickle path
                    integer = int(name.rstrip('.pickle').split('_')[1])
                    if (integer%doses) +1 == dose:
                    	pickle_pwd = os.path.join( still_dir, name )
                    	# inputs pickle_pwd into np array
                        jar = pickle.load(open(pickle_pwd, 'r'))
                        unit_cell_ob=jar['observations'][0].unit_cell().parameters()[0]
                        if unit_cell_target == 'Big':
                            if unit_cell_ob > unit_cell_cutoff:
	                    	pickle_list_1 = np.array( [ [ pickle_pwd ] ] )
        	            	pickle_list = np.concatenate( ( pickle_list, pickle_list_1 ), axis=1 )
                        else:
                            if unit_cell_ob < unit_cell_cutoff:
	                    	pickle_list_1 = np.array( [ [ pickle_pwd ] ] )
        	            	pickle_list = np.concatenate( ( pickle_list, pickle_list_1 ), axis=1 )
                else:
                    pickle_pwd = os.path.join( still_dir, name )
                    # inputs pickle_pwd into np array
                    print pickle_pwd
                    jar = pickle.load(open(pickle_pwd, 'r'))
                    unit_cell_ob=jar['observations'][0].unit_cell().parameters()[0]
                    if unit_cell_target == 'Big':
                       if unit_cell_ob > unit_cell_cutoff:
	                   pickle_list_1 = np.array( [ [ pickle_pwd ] ] )
        	           pickle_list = np.concatenate( ( pickle_list, pickle_list_1 ), axis=1 )
                       elif unit_cell_ob == unit_cell_cutoff:
                            print('CELL')
                    else:
                        if unit_cell_ob < unit_cell_cutoff:
	                    pickle_list_1 = np.array( [ [ pickle_pwd ] ] )
        	            pickle_list = np.concatenate( ( pickle_list, pickle_list_1 ), axis=1 )
    # returns single column np array of int_pwds
    return pickle_list
 
def main( args ):
    # cols for still_dirs df
    cols = [ "still_dir" ]
    # if -l
    if args.input_list:
        still_dirs = args.input_list
        still_df = pd.read_csv( still_dirs, names=cols )
    elif args.stills_directory:
        still_dir = [ args.stills_directory ]
        still_df = pd.DataFrame( still_dir, columns=cols )
    # empty np array for pickles
    pickle_list = np.array( [ [ ] ] )
    print "dir searching for int files:"
    for still_dir in still_df[ "still_dir" ]:
        print still_dir
        if args.unit_cell:
           print args.unit_cell
           pickle_list_1 = get_int_pickles_uc(still_dir,unit_cell_cutoff=args.unit_cell_cutoff, unit_cell_target=args.unit_cell_target, dose=args.dose, doses=args.total_dose)
        else:
           pickle_list_1 =  get_int_pickles( still_dir, args.dose, args.total_dose )
        pickle_list = np.concatenate( ( pickle_list, pickle_list_1 ), axis=1 )
        print "done"
    pickle_list = np.transpose( pickle_list )
    pickle_len = len( pickle_list )
    if args.no_of_images:
        images = args.no_of_images
    else:
        images = pickle_len
    cols = [ "still_pwd" ]
    pickle_df = pd.DataFrame( pickle_list, columns=cols )
    sample_df = pickle_df.sample( images )
    if args.unit_cell and not args.dose:
       file_name = "{2}_{0}_images_unit_cell_{1}.dat".format( images, args.unit_cell_target,  args.stills_directory.split('/')[-1]) 
    elif args.dose and args.unit_cell:
       file_name = "prime_input_{0}_images_unit_cell_{2}_dose_{1}.dat".format( images, args.dose, args.unit_cell_target )
    elif args.dose:
       file_name = "prime_input_{0}_images_dose_{1}.dat".format( images, args.dose )
    else:
	file_name = "prime_input_{0}_images.dat".format( images )
    sample_df.to_csv( file_name, header=False, index=False )
 
args = argarser()
main( args )
