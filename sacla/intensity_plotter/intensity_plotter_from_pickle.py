 # -*- coding: utf-8 -*-

import pickle
import os
import matplotlib.pyplot as plt

def get_ints(fid_list):
    for fid in fid_list:
        jar = pickle.load(open(dir+fid, 'r'))
        obs = jar['observations'][0]
        for o in obs.resolution_filter(d_max=1.81,d_min=1.78):
            yield o[1]

dir = "/dls/x02-1/data/2017/mx15722-8/processing/danny/dials/berlin-0-completed/"
#'/dls/i24/data/2017/nt14493-63/processing/scripts/experiment_refinement_process_test_folder/waylinCD/'
file_list = [fid for fid in os.listdir(dir) if fid.startswith('int-') and fid.endswith('.pickle')]
int_bin_dict = {}
list_of_ints= list(get_ints(file_list))  

plt.hist(list_of_ints, bins=300)
plt.show()
