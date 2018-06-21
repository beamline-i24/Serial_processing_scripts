import pickle
import sys
import os
from dials.util.options import flatten_reflections
from dials.util.phil import ReflectionTableConverters
converter = ReflectionTableConverters()

def print_flush(string):
    sys.stdout.write('\r%s' % string)
    sys.stdout.flush()

def get_list(directory, wild):
    list_of_files = sorted([pickle.split('_')[-2] for pickle in os.listdir(directory) if pickle.endswith(wild)])
    return list_of_files

def filter_im_nums(strong_files, indexed_files):
    return  filter(lambda indexed_files: indexed_files in strong_files, indexed_files) 

def get_file_names(img_num): 
    strong = 'idx-weezer0044_%s_strong.pickle'%img_num
    indexed = 'idx-weezer0044_%s_indexed.pickle'%img_num
    integrated = 'int-0-weezer0044_%s.pickle'%img_num
    return (strong, indexed, integrated)

def get_reflection_list(directory, file_name):
    reflection_list=[]
    reflection_list.append(converter.from_string(os.path.join(directory,file_name)))
    return reflection_list

def flatten_list(reflection_list):
    return flatten_reflections(reflection_list)

def sum_list(reflections):
    length_list= [len(rlist) for rlist in reflections] 
    return float(sum(length_list))

def check_for_int(name):
    if os.path.isfile(name):
       return name
    else:
       return None

def get_ratio(strong, indexed, directory):
    strong_reflections=flatten_reflections(get_reflection_list(directory, strong))
    indexed_reflections=flatten_reflections(get_reflection_list(directory,indexed))
    strong_val=sum_list(strong_reflections)
    indexed_val=sum_list(indexed_reflections)
    return (indexed_val/float(strong_val))*100
    

def main():
    #directory='/dls/i24/data/2018/nt14493-94/processing/stills_process/dtpaa/fugees1234_jr_2'
    directory='/dls/i24/data/2018/nt14493-94/processing/stills_process/acnir/weezer123_jr/00000-32000'
    print 'list files'
    indexed_files = get_list(directory, wild='indexed.pickle')
    strong_files = get_list(directory,wild='strong.pickle')
    print 'filter strong by indexed'
    strong_indexed_files = filter_im_nums(strong_files, indexed_files) 
    out_list = []
    for c, img_num in enumerate(strong_indexed_files):
        s = '%04d:%04d %02d%%  ' % (c, len(strong_indexed_files), 100*float(c)/len(strong_indexed_files))
        print_flush(s)
        strong, indexed, integrated = get_file_names(img_num)
        string=check_for_int(os.path.join(directory,integrated))
        ratio=get_ratio(strong, indexed, directory)
        out_list.append('%05d    %f    %s \n'%(int(img_num), ratio, string))
        #print('indexed to strong spot ratio = %f percent'%(100*ratio))
    with open('spot_ratio_test.dat','w') as f:
	f.write('image_number strong/indexed_spots(%) integrated_file \n')
        for item in out_list:
           f.write("%s" % item)

if __name__ == '__main__':
    main()
