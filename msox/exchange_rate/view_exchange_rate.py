#Author: Darren Sherrell
#Edit: Martin Appleby

import sys
import numpy as np
import scipy as sc
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import argparse
from scipy.interpolate import UnivariateSpline

def argparser(argv=None):
    parser = argparse.ArgumentParser(description = 'Exchange Rate Viewer\n\
	                                 Plots the Number of images per dose per unit cell. \
                                         ./exchange_rate_viewer.py -i pacman_igypop5678_ucs_all_1.dat -uc 97.25 -d 10')
    parser.add_argument("-i","--input_file", type=str,
	                    help="pacman.dat file", default=None)
    parser.add_argument("-o","--output", type=str,
	                    help="graph title and file name", default=None)
    parser.add_argument("-uc","--unit_cell", type=float,
			    help="median value between two unit cells", default=0.0)
    parser.add_argument("-d","--doses", type=float,
			    help="Number of doses in dataset", default=10)
    parser.add_argument("-s","--save", type=bool,
			    help="AutoSave graph", default=False)
    parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2],
	                    help="increase output verbosity")
    args = parser.parse_args()
    if not args.input_file:
       msg="Need input file!!!!!!!!!!"
       raise argparse.ArgumentTypeError(msg)
    elif args.directory or args.directory_list:
	pass 	
    return args

def get_values(fid, unit_cell=0.0, doses = 10):
    print fid
    num_of_doses = doses #20
    data_dict = {}
    for x in range(num_of_doses):
        data_dict[x] = [[],[]]
    f = open(fid, 'rU')
    for line in f.readlines():
        if not line.startswith('int-'):
            continue
        line.rstrip('\n')
        entry = line.split()
        img_num = int(entry[0].split('_')[1].split('.')[0])
        dose = img_num % num_of_doses 
        val = float(entry[1])
        if val > unit_cell:
            data_dict[dose][0].append(val)
        else:
            data_dict[dose][1].append(val)
    return data_dict

def main(args):
    fid = args.input_file
    cutoff=args.unit_cell
    doses = args.doses
    save = args.save
    fig = plt.figure()
    fig.subplots_adjust(left   = 0.05,
                        bottom = 0.05,
                        right  = 0.95, 
                        top    = 0.95,
                        wspace = 0.00, 
                        hspace = 0.00)
    colors = ['r', 'b', 'k', 'y', 'b', 'g', 'm']
    #lab = fid_list[i][:3].upper()
    #lab = fid_list[i]
    ax = fig.add_subplot(111, axisbg='beige')
    data_dict = get_values(fid, cutoff, doses)
    for dose, data_list in data_dict.items():
        print dose, len(data_list[0]), len(data_list[1])
        if dose == 0:
            ax.plot(dose, len(data_list[0]), marker='o', c='r', label='Above')
            ax.plot(dose, len(data_list[1]), marker='o', c='b', label='Below')
            ax.plot(dose, len(data_list[0])+len(data_list[1]), 'o', c='k', label='Total')
        else:
            ax.plot(dose, len(data_list[0]), marker='o', c='r')
            ax.plot(dose, len(data_list[1]), marker='o', c='b')
            ax.plot(dose, len(data_list[0])+len(data_list[1]), 'o', c='k')
    plt.xlim(-1, 10)
    if args.output:
       title = args.output
       output_file='%s.fig'%title
    else:
       title=input_file
       output_file='out.fig'
    plt.title('Exchange Rate of %s above/below %0.2fA'%(title, cutoff))
    plt.xlabel('Dose/Image')
    plt.ylabel('Total Number')
    leg = plt.legend(loc='lower left', title='Group', fancybox=True)
    if save:
       plt.savefig(output_file) 
    #frame = leg.get_frame()
    #frame.set_facecolor('beige')

if __name__ == '__main__':
   args = argparser()
   main(args)
   plt.show()
   plt.close()
