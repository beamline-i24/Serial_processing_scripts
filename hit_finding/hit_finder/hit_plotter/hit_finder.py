#!/dls_sw/apps/dials/dials-v1-9-3/build/bin/dials.python

import pickle
import sys
import os
import heapq
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.colors as colors
import matplotlib.cm as cm
import argparse
import matplotlib.animation as animation
import json

import hit_calculator as hc
import hit_plotter as hit_plot
import file_searcher as fs
from reflections import *
import hit_finder_tools as ht

last_index = 0

fig = plt.figure(figsize=(17,17))#facecolor='0.3', figsize=(17,17))
ax1 = fig.add_subplot(111)#, axisbg='k')
fig.subplots_adjust(left=0.05,bottom=0.05,right=0.95,top=0.95)

def argparser(argv=None):
    parser = argparse.ArgumentParser(description = 'Hit Finder\n\
	                                 Analyses spot count data to produce an estimate\
	                                 of the hit rate for a given directory.\n\
	                                 EXAMPLE\n ./hit_finder.py')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument("-i" ,"--input_file", type=str, required=True,
	                    help="set input file e.g. /dls/ixx/data/xxxx/xxxxxx-xx/processing/image_analysis/name/name.out")
    parser.add_argument("-r","--run_number", type=int,
			help="chip run number")
    parser.add_argument("-sc","--spot_count_cutoff", type=int, default = 16,
			help="spot_count_threshold, default= 16")
    parser.add_argument("-lc","--log_spot_cutoff", type=int, default = 15,
			help="spot_count_threshold, default= 15")
    parser.add_argument("-dm","--d_min_cutoff", type=float, default = None,
			help="max resolution for image to be processed, default=cbf header resolution")
    parser.add_argument("-p","--process_type",type=str, default = 'live', choices = ['live', 'client', 'pickle', 'compare', 'index', 'jlive'],
                            help="client runs spot_find client to calculate hit_rate, pickle reads values from strong.pickle files")
    parser.add_argument("-pl","--plot",type = bool, default = False,
                            help="enable plots for certain process_types")
    parser.add_argument("-pd","--processed_directory",type=str, default = None,
                            help="only needed for proc_type compare, set processed directry location/location of int-files i.e. /dls/ixx/data/xxxx/xxxxxx-xx/processing/name/")
    parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2],
	                    help="increase output verbosity")
    args = parser.parse_args()
    if args.process_type == 'compare' and not args.processed_directory:
       parser.error("must have processed_directory -pd ")
    elif args.processed_directory and args.process_type != 'compare':
       print("redundant variable: -pd processed_directory only used for process type compare")
    return args

def print_flush(string):
     sys.stdout.write('\r%s' % string)
     sys.stdout.flush()

def from_pickle(args):
    print 'list files'
    directory=args.processed_directory
    strong_spot_cutoff = args.spot_count_cutoff
    strong_files = fs.get_list(directory,wild='strong.pickle')
    indexed_files = fs.get_list(directory, wild='indexed.pickle')
    print 'filter strong by indexed'
    hits, actual_hits = 0, 0
    actual_hit_list = []
    out_array=[]
    for c, img_num in enumerate(strong_files[:]):
        s = '%04d:%04d %02d%%  ' % (c, len(strong_files), 100*float(c)/len(strong_files))
        ht.print_flush(s)
        strong, indexed, integrated, int_1, int_2 = fs.get_file_names(directory, img_num)
        strong=strong[0]
        if integrated:
           integrated=integrated[0]
           indexed=indexed[0]
           actual_hits+=1
           #int_reflections=get_num_reflections(integrated, directory)
           indexed_reflections, total_intensity=get_num_reflections(indexed, directory)
           if int_1:
              if int_2:
                 actual_hit=3
              else: 
                 actual_hit=2
           else:
               actual_hit=1
        else:
	   actual_hit=0
           int_reflections=0
           indexed_reflections=0
        strong_num, total_intensity=get_num_reflections(strong, directory)
        if strong_num > strong_spot_cutoff:
            hits+=1
            est_hit=1
            if indexed_reflections != 0:
               spot_ratio=indexed_reflections/float(strong_num)
               print spot_ratio
            else:
               spot_ratio=0
        else:
            est_hit=0
            spot_ratio=0
        out_array.append([img_num, strong_num, total_intensity, actual_hit, est_hit, spot_ratio])
    print('estimated hit_rate = %f'%((float(hits)/len(strong_files))*100))
    print('actual hit_rate = %f'%((float(actual_hits)/len(strong_files))*100))
    np_array = np.array(out_array)
    hit_plot.pickle_ratio_plot(np_array)
    return np_array

def intensity_client(args):
    input_file = args.input_file
    processed_directory = args.processed_directory
    plot = args.plot
    if args.process_type == 'compare':
       compare = True
    else:
       compare = False

    np_array, total = fs.file_search(input_file, processed_directory=processed_directory, compare = compare)
    if plot:
       hit_plot.compare_hits_plot(np_array, compare)
    hit_count, hit_images = hc.client_calculator(np_array, compare, args)
    
    print('estimated counts rate = %f'%(float(hit_count*100/float(total))))
    if compare:
       print('single_lattice only rate = %f'%(float(len(hits)*100/float(total))))
       print('all hits rate = %f'%(float(len(total_hits)*100/float(total))))
       hit_count = 0
       for image, hit in hit_images:
           if hit > 0:
              hit_count+=1
       print len(hit_images), hit_count, len(total_hits)

    return np_array

def spot_client_index(args):
    input_file = args.input_file
    processed_directory = args.processed_directory
    plot = args.plot

    np_array, total = fs.file_search(input_file, processed_directory=processed_directory, compare = True, indexed=True)
    if plot:
       hit_plot.compare_hits_plot(np_array, compare)
    hit_count, hit_images = hc.client_calculator(np_array, compare, args)
    
    print('estimated counts rate = %f'%(float(hit_count*100/float(total))))
    if compare:
       print('single_lattice only rate = %f'%(float(len(hits)*100/float(total))))
       print('all hits rate = %f'%(float(len(total_hits)*100/float(total))))
       hit_count = 0
       for image, hit in hit_images:
           if hit > 0:
              hit_count+=1
       print len(hit_images), hit_count, len(total_hits)

    return np_array

def animate_json(i,args):
    global last_index
    d_min_cutoff = args.d_min_cutoff 
    spot_count_cutoff = args.spot_count_cutoff
    log_spot_cutoff = args.log_spot_cutoff
    input_file = args.input_file
    print('loading file')
    print('updating plot')
    out_array=[]
    with open(input_file, 'r') as f:
         data = json.load(f)
    for i, record in enumerate(data):
        print_flush(str(i))
        image_num=record['image'].split('_')[1].split('.')[0]
        strong=record['n_spots_total']
        intensity=record['total_intensity']
        if float(record['total_intensity']) <= 0 or int(record['n_spots_no_ice']) <= 0:
           ratio=0
        else:
           ratio=(float(record['total_intensity'])/float(record['n_spots_no_ice']))
        noise_1 = record['noisiness_method_1']
        noise_2 = record['noisiness_method_2']
        d_min = record['d_min']
        d_min_1 = record['d_min_1']
        d_min_2 = record['d_min_2']
        out_array.append([image_num, ratio, intensity, strong, noise_1, noise_2, d_min, d_min_1, d_min_2])
        np_array = np.array(out_array)
        cNorm  = colors.Normalize(vmin=0, vmax=1)
        scalarMap = cm.ScalarMappable(norm=cNorm, cmap=cm.seismic) 
        colours = []
        hits = []
        hit_images = []
        hit_count = 0
        indexable_images = []
        for num, ratio, intensity, strong,  noise_1, noise_2, d_min, d_min_1, d_min_2 in np_array:
            if strong >= spot_count_cutoff:
              indexable_images.append(num)
              if ratio >= 10:
                 if  0.0 <= noise_1 <= 0.875:
                    if 0.0 <= noise_2 <= 0.96:
                         hit_images.append([num, strong])
                         colours.append(scalarMap.to_rgba(1))
                         hit_count+=1
                    else:
                       hits.append(0) 
                       colours.append(scalarMap.to_rgba(0))
                 else:
                   hits.append(0) 
                   colours.append(scalarMap.to_rgba(0))
              else:
                hits.append(0) 
                colours.append(scalarMap.to_rgba(0))
            else:
               hits.append(0) 
               colours.append(scalarMap.to_rgba(0))
        if hit_count > 0 and total > 0: 
           print('estimated counts rate = %f'%(float(hit_count*100/float(total))))
        print('number of potential indexable images =  %d'%(len(indexable_images)))
        if len(indexable_images) > 0 and hit_count > 0:
           print('estimated hit_rate from indexable images = %f'%(float(hit_count)*100/float(len(indexable_images))))
        #hit_array = np.array(hit_images)
        print heapq.nlargest(10, hit_images, key=lambda x: x[1])
        ax1.scatter(image_numbers[last_index:], spot_counts[last_index:],  c=colours[last_index:], cmap=cm.seismic)
        last_index=len(image_numbers)
        #a,b = np.polyfit(np.log(intensities),spot_counts,1, w=np.sqrt(spot_counts))
        out_file=input_file.split('.')[0]
        with open(out_file+'.hits','w') as hit_file:
             for image, spot in hit_images:
                 hit_file.write(str(int(image)) + '\n')


def animate(i, args):    
    global last_index
    d_min_cutoff = args.d_min_cutoff 
    spot_count_cutoff = args.spot_count_cutoff
    log_spot_cutoff = args.log_spot_cutoff
    input_file = args.input_file
    print('loading file')
    print('updating plot')
    np_array, total=fs.file_search(input_file)
    image_numbers, intensities, blank, spot_counts, a4_spots = np_array[:,0], np_array[:,1], np_array[:,2], np_array[:,3], np_array[:,4]
    cNorm  = colors.Normalize(vmin=0, vmax=1)
    scalarMap = cm.ScalarMappable(norm=cNorm, cmap=cm.seismic) 
    colours = []
    hits = []
    hit_images = []
    hit_count = 0
    indexable_images = []
    for num, i, hit, strong, high, noise_1, noise_2, d_min, d_min_1, d_min_2 in np_array:
        if strong >= spot_count_cutoff:
          indexable_images.append(num)
          if i > 0:
            if float(i)/strong > 10:
             if  0.0 <= noise_1 <= 0.875:
                if 0.0 <= noise_2 <= 0.96:
                     hit_images.append([num, strong])
                     colours.append(scalarMap.to_rgba(1))
                     hit_count+=1
                else:
                   hits.append(0) 
                   colours.append(scalarMap.to_rgba(0))
             else:
               hits.append(0) 
               colours.append(scalarMap.to_rgba(0))
          else:
            hits.append(0) 
            colours.append(scalarMap.to_rgba(0))
        else:
           hits.append(0) 
           colours.append(scalarMap.to_rgba(0))
    if hit_count > 0 and total > 0: 
       print('estimated counts rate = %f'%(float(hit_count*100/float(total))))
    print('number of potential indexable images =  %d'%(len(indexable_images)))
    if len(indexable_images) > 0 and hit_count > 0:
       print('estimated hit_rate from indexable images = %f'%(float(hit_count)*100/float(len(indexable_images))))
    #hit_array = np.array(hit_images)
    print heapq.nlargest(10, hit_images, key=lambda x: x[1])
    ax1.scatter(image_numbers[last_index:], spot_counts[last_index:],  c=colours[last_index:], cmap=cm.seismic)
    last_index=len(image_numbers)
    #a,b = np.polyfit(np.log(intensities),spot_counts,1, w=np.sqrt(spot_counts))
    out_file=input_file.split('.')[0]
    with open(out_file+'.hits','w') as hit_file:
         for image, spot in hit_images:
             hit_file.write(str(int(image)) + '\n')
               
if __name__ == '__main__':
    args = argparser()
    if args.process_type=='pickle':
    	from_pickle(args)
    elif args.process_type == 'client':
        intensity_client(args)
        plt.show()
    elif args.process_type == 'jlive':
        plt.axhline(args.spot_count_cutoff)
        ani = animation.FuncAnimation(fig, animate_json, fargs=(args, ), interval=5000, frames=100000)
        print ani, type(ani)
        plt.show()
    elif args.process_type == 'live':
        plt.axhline(args.spot_count_cutoff)
        ani = animation.FuncAnimation(fig, animate, fargs=(args, ), interval=5000)
        print ani, type(ani)
        plt.show()
    elif args.process_type == 'index':
        spot_client_index(args)
        plt.show()
    elif args.process_type == 'compare':
        intensity_client(args)
        plt.show()
    else:
        print('undidentified process type: ' + args.process_type)

