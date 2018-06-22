#!/usr/bin/python
import os
import re
import sys
import math
import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit
from scipy.stats import norm
from scipy import asarray as ar,exp

def make_big_list(in_fid):
    big_list = []
    f = open(in_fid, 'r')
    for line in f.readlines():
        entry = line.split()
        listy = entry[2]
        big_list.append(listy)
    return big_list

def gaus(x,a,x0,sigma):
    return a*exp(-(x-x0)**2/(2*sigma**2))

def main(in_fid):
    big_list = make_big_list(in_fid)
    
    test_list = [float(x) for x in big_list]
    print test_list
    m,s = norm.fit(test_list)
    n = len(test_list) 
    x = ar(range(n))
    y = ar(test_list)
    """
    n = len(test_list) 
    x = ar(range(n))
    y = ar(test_list)
    mean = sum(x * y) / n 
    sigma = np.sqrt(sum(y * (x - mean)**2) / n)       

    #popt ,pcov = curve_fit(gaus, x, y, p0=[max(y), mean, sigma]) 
    """
    popt ,pcov = curve_fit(gaus, x, y, p0=[203, m, s]) 
    print popt 
    #plt.plot(x, y)
    plt.plot(x,gaus(x,*popt),'ro:',label='fit')
    plt.show()
    
if __name__ == '__main__':
    main(sys.argv[1])
plt.close()
