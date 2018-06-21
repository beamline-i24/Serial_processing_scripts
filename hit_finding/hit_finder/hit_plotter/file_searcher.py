import numpy as np
import re
import glob
import os

import hit_finder_tools as ht

spot_count= re.compile(r'<spot_count_no_ice>(\d+)</spot_count_no_ice>')
n_indexed= re.compile(r'<n_indexed>(\d+)</n_indexed>')
spot_count_4A = re.compile(r'<spot_count_4A>(\d+)</spot_count_4A>')
total_intensity= re.compile(r'<total_intensity>(\d+)</total_intensity>')
image_finder= re.compile(r'<file-pattern-index>(\d+)</file-pattern-index>')
file_finder= re.compile(r'<file>(.*)</file>')
spot_ice = re.compile(r'<spot_count>(\d+)</spot_count>')
d_min_finder =  re.compile(r'<d_min>([+-]?\d+\.\d+)</d_min>')
d_min_1_finder = re.compile(r'<d_min_method_1>([+-]?\d+\.\d+)</d_min_method_1>')
d_min_2_finder = re.compile(r'<d_min_method_2>([+-]?\d+\.\d+)</d_min_method_2>')
noise_1_finder = re.compile(r'<noise_1>([+-]?\d+\.\d+)</noise_1>')
noise_2_finder = re.compile(r'<noise_2>([+-]?\d+\.\d+)</noise_2>')
fraction_indexed = re.compile(r'<fraction_indexed>([+-]?\d+\.\d+)</fraction_indexed>')

def filter_lists(indexed_files, strong_files):
    return  filter(lambda indexed_files: indexed_files in strong_files, indexed_files) 

def get_run_number(input_directory):
    run_file = [fil for fil in os.listdir(input_directory) if fil.endswith('00000.cbf')]
    run_number = int(runfile[0].split(chip_name)[1].split('_')[0])
    return run_number

def get_list(directory, wild):
    list_of_files = sorted([pickle.split('_')[-2] for pickle in os.listdir(directory) if pickle.endswith(wild)])
    return list_of_files

def check_for_file(name):
    if os.path.isfile(name):
       return name
    else:
       return None

def line_search(pattern, line):
    pattern_search = pattern.search(line)
    if pattern_search:
       output = pattern_search.group(1)
    else:
       output = None
    return output

def get_file_names(directory, current_image):
    current_image=int(current_image)
    strong = glob.glob(os.path.join(directory,"*%05d*strong.pickle"%current_image))
    indexed = glob.glob(os.path.join(directory,"*%05d*indexed.pickle"%current_image))
    int_0 = glob.glob(os.path.join(directory,"int-0*%05d*"%current_image))
    int_1 = glob.glob(os.path.join(directory,"int-1*%05d*"%current_image))
    int_2 = glob.glob(os.path.join(directory,"int-2*%05d*"%current_image))
    return strong, indexed, int_0, int_1, int_2

def int_search(directory, current_image):
    strong, indexed, integrated, int_1, int_2 = get_file_names(directory,current_image)
    if integrated:
       if int_1:
         if int_2:
            hit=3
         else: 
            hit=2
       else:
            hit=1
    else:
       hit=0
    return hit

def file_search(input_file, processed_directory=None, compare = False, indexed = False):
    total = 0
    out_array = []
    with open(input_file,'r') as input_file:
       for line in input_file:
          line_check = line
          image = line_search(image_finder, line_check)
          if image:
	      current_image = "%05d"%(int(image.split('_')[-1].split('.')[0]))
              ht.print_flush(current_image)
              if compare:
                 hit = int_search(processed_directory, current_image) 
              else:
                 hit = None
              total += 1
              continue
          spot_search = line_search(spot_ice, line_check)
          if spot_search:
             strong_num = int(spot_search)
             continue
          res_spot_search = line_search(spot_count_4A, line_check)
          if res_spot_search:
             high_spots = int(res_spot_search)
             continue
          d_min_search = line_search(d_min_finder, line_check)
          if d_min_search:
                 d_min= float(d_min_search)
                 continue
	  d_min_method_1_search = line_search(d_min_1_finder, line_check)
          if d_min_method_1_search:
                 d_min_1 = float(d_min_method_1_search)
                 continue
	  d_min_method_2_search = line_search(d_min_2_finder, line_check)
          if d_min_method_2_search:
                 d_min_2 = float(d_min_method_2_search)
                 continue
          noise_1_search = line_search(noise_1_finder, line_check)
          if noise_1_search:
             noise_1 = float(noise_1_search)
          noise_2_search = line_search(noise_2_finder, line_check)
          if noise_2_search:
             noise_2 = float(noise_2_search)
          intensity_search = line_search(total_intensity, line_check)
          if intensity_search:
             tot_int=intensity_search
             if not indexed:
                if current_image is None:
                     continue
                else:
                   out_array.append([int(current_image), float(tot_int), hit, int(strong_num), int(high_spots), noise_1, noise_2, d_min, d_min_1, d_min_2])
                
          if indexed:
             fraction_search = line_search(fraction_indexed, line_check)
             if fraction_search:
                fraction = fraction_search
                continue
             indexed_search = line_search(n_indexed, line_check)
             if indexed_search:
                indexed_num=indexed_search
                if current_image is None:
                     continue
                else:
                   out_array.append([int(current_image), float(tot_int), hit, int(strong_num), int(high_spots), noise_1, noise_2, d_min, d_min_1, d_min_2, float(fraction), int(indexed_num)])
    out_array = np.array(out_array)
    return out_array, total 


