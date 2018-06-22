import pickle
import os
import sys


def test_look():
    path = '/dls/i24/data/2017/nt14493-63/processing/integrated/waylinCD/dose20/'
    fid = 'int-0-waylinCD0077_99759.pickle'
    jar = pickle.load(open(path+fid, 'r'))
    for onion in jar:
        print onion
    obs = jar['observations'][0]
    #print dir(obs)
    print obs.show_summary()
    print obs.unit_cell().volume()


def list_searcher(directory, wild='int-0'):
    search_list = []
    for fid in os.listdir(directory):
        if wild in fid:
            if fid.endswith('pickle'):
                integer = int(fid.rstrip('.pickle').split('_')[1])
                search_list.append(integer)
            elif fid.endswith('json'):
                integer = int(fid.rstrip('.json').split('_')[1])
                search_list.append(integer)
    return sorted(search_list)


def find_contiguous(chip_name='waylinAB', doses=10, contiguous_limit=8,
                     path='/dls/i24/data/2017/nt14493-63/processing/stills_process/', wild='int-0'):
    #directory = path + chip_name
    directory = path
    print 30*'*', '\n', directory, '\n', 30*'*'
    img_num_list = list_searcher(directory, wild='int-0')
    print 'First 50 imgs', img_num_list[:50]
    num_of_sets = 0
    k_counter = 1
    starts_list = []
    for i, img_num in enumerate(img_num_list[:-1]):
        try:
            # Test contiguousness
            if (img_num_list[i + 1] - img_num_list[i]) == 1:
                k_counter += 1
            # If the contiguousness stops less than contiguous_limit
            # Reset countigous counter and start over
            elif k_counter < contiguous_limit:
                k_counter = 1
                continue
            # If contiguousness stops but the counter is equal or greater than
            # the contiguous limit calculate start image
            else:
                start_img = img_num - k_counter + 1
                # print start_img, k_counter
                next_img = start_img
                countdown = k_counter
                for j in range(k_counter):
                    next_img += 1
                    countdown -= 1
                    if (next_img % doses) == 1:
                        if countdown - (next_img % doses) >= contiguous_limit - 2:
                            # print '-->', next_img, countdown
                            num_of_sets += 1
                            starts_list.append(next_img - 1)
                k_counter = 1
        except StandardError, e:
            print e

    print '\nNumber of imgs', len(img_num_list)
    print 'Number of sets', num_of_sets
    print 'Percent', int(100 * (contiguous_limit * float(num_of_sets)) / len(img_num_list))
    return starts_list


def find_experiments_json_starts(chip_name='waylinCD', doses=20, before_limit=5,
                                                    path='/dls/i24/data/2017/nt14493-63/processing/stills_process/'):
    directory = path + chip_name
    print directory
    img_num_list = list_searcher(directory, wild='experiments.json')
    experiments_json_list = []
    start_list = []
    for img_num in img_num_list[:]:
        try:
            if img_num % doses <= before_limit:
                start = img_num - (img_num % doses)
                if start in start_list:
                    continue
                else:
                    experiments_json_list.append(img_num)
                    start_list.append(start)
        except StandardError, e:
            print e
    print '\nNumber of imgs', len(img_num_list)
    print 'Number of sets', len(experiments_json_list)
    print 'Percent', int(100 * ((doses * len(experiments_json_list)) / len(img_num_list)))
    return experiments_json_list

def main(*args):
    #currently only uses type and searches waylinCD only
    args_dict = {'type':None,'path':None, 'chip_name':None, 'doses':None, 'contiguous_limit':None, 'before_limit':None}
    for arg in args:
        k = arg.split("=")[0]
        v = arg.split("=")[1]
        print "Keyword argument: %s=%s" % (k, v)
        there = [True for key in args_dict.keys() if k in key]
        if True not in there:
            print 'Unknown arg in args:', arg
            print 'Allowed Keywords:', args_dict.keys()
            print 'Exiting'
            return 0
        else:
            args_dict[k] = v

    if args_dict['type'] == 'contiguous':
        starts_list = find_contiguous(chip_name ='waylinCD', doses=20, contiguous_limit=10)
        pickle.dump(starts_list, open('john.pickle','w') )
        print starts_list
    elif args_dict['type'] == 'starts':
        xpmts_json_list = find_experiments_json_starts('waylinCD', doses=20, before_limit=5)        
        pickle.dump(starts_list, open('john.pickle','w') )
        print xpmts_json_list
    else:
        print(type, 'type not recognised. AVailable types: starts, contiguous')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print '\n\t\t\t\tNEST'
        print "\t\t\t\tEXAMPLE\n ./nest.py type=contiguous path=/dls/i24/data/2017/nt14493-63/processing/stills_process/ \
                                    chip_name=waylinCD doses = 20 contiguous_limit =10 \n"
        print "\t\t\t\tEXAMPLE\n ./nest.py type=starts path=/dls/i24/data/2017/nt14493-63/processing/stills_process/ \
                                    chip_name=waylinCD doses = 20 before_limit =10 \n"
        print '\t\t\t\tDOCUMENT\n https://docs.google.com/document/d/1osARU4TDkosdJZIhcILc7v_foH-4pCearg71k3Nrhg4/edit#heading=h.3n4jjttquv3z \n\n'
    else:
        main(*sys.argv[1:])
