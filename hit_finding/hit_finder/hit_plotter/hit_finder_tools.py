import numpy as np
from sys import stdout

def get_h(h):
    golden_ratio_conjugate = 0.618033988749895
    h += golden_ratio_conjugate
    h % 1 
    return h

def log_fit(x,y):
    #print x,y
    a,b = np.polyfit(np.log(x),y,1, w=np.sqrt(y))
    return a*np.log(np.unique(x))+b

def print_flush(string):
    stdout.write('\r%s' % string)
    stdout.flush()

def split_zocalo_array(np_array):
    image_numbers=np_array[:,0]
    intensities=np_array[:,1]
    hits=np_array[:,2]
    strong=np_array[:,3]
    high=np_array[:,4]
    noise_1=np_array[:,5]
    noise_2=np_array[:,6]
    d_min=np_array[:,7]
    d_min_1=np_array[:,8]
    d_min_2=np_array[:,9]
