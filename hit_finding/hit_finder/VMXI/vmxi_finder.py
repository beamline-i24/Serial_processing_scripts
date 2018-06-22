import numpy as np
import matplotlib.pyplot as plt
import re
import argparse

image_finder= re.compile(r'<file-pattern-index>(\d+)</file-pattern-index>')
spot_count= re.compile(r'<spot_count_no_ice>(\d+)</spot_count_no_ice>')
spot_ice= re.compile(r'<spot_count>(\d+)</spot_count>')
total_intensity= re.compile(r'<total_intensity>(\d+)</total_intensity>')


def argparser(argv=None):
    parser = argparse.ArgumentParser(description = 'Hit Finder\n\
	                                 Analyses spot count data to produce an estimate\
	                                 of the hit rate for a given directory.\n\
	                                 EXAMPLE\n ./hit_finder.py')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument("-i" ,"--input_file", type=str, required=True)
    parser.add_argument("-c" ,"--spot_count_cutoff", type=int, default=30)
    parser.add_argument("-s" ,"--show_fig", type=bool, default=False)
    args = parser.parse_args()
    return args

def line_search(pattern, line):
    pattern_search = pattern.search(line)
    if pattern_search:
       output = pattern_search.group(1)
    else:
       output = None
    return output


def file_search(input_file, processed_directory=None, compare = False):
    total = 0
    out_array = []
    with open(input_file,'r') as input_file:
       for line in input_file:
          line_check = line
          image = line_search(image_finder, line_check)
          if image:
	      current_image = "%05d"%(int(image.split('_')[-1].split('.')[0]))
              total += 1
              continue
          spot_search = line_search(spot_count, line_check)
          if spot_search:
             strong_num = int(spot_search)
             continue
          spot_ice_search = line_search(spot_ice, line_check)
          if spot_ice_search:
             all_spots = int(spot_ice_search)
             continue
          intensity_search = line_search(total_intensity, line_check)
          if intensity_search:
             if current_image is None:
                   continue
             else:
                 out_array.append([int(current_image), float(intensity_search), int(strong_num), int(all_spots)])
    out_array = np.array(out_array)
    return out_array, total 

def main(input_file, spot_count_cutoff=30, show_fig=False):
    array, total=file_search(input_file)
    rate=0
    hit_count=0
    hit_images = []
    strong_im = 0
    average_im = 0
    for num, i, strong, all_spots in array:
        if all_spots > 0:
           strong_im += all_spots
           average_im += 1
        if all_spots >= spot_count_cutoff:
           hit_count+=1
           hit_images.append(num)
    print('estimated counts rate = %f'%(float(hit_count*100/float(total))))
    print('average_non_zero_count = %f'%(int(strong_im/float(average_im))))
    print('average_non_zero_images_used = %f'%(average_im))
    plt.scatter(array[:,0], array[:,3])
    plt.savefig(input_file.split('.')[0]+'.png')
    if show_fig:
       plt.show()
    with open('{}_hits.dat'.format(input_file.split('.')[0]), 'w') as out_file:
         for image in hit_images:
               out_file.write('{} \n'.format(str(image)))
    return array

if __name__ == '__main__':
   args=argparser()
   input_file=args.input_file
   spot_count_cutoff=args.spot_count_cutoff
   show_fig=args.show_fig
   out_array = main(input_file, spot_count_cutoff, show_fig)
    
