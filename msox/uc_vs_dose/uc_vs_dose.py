from scipy.optimize import curve_fit
from scipy.stats import norm
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.mlab as mlab
import sys

def gauss_func(x, sig, mu):
    return (1/(sig * (2*np.pi)**.5)) * np.e**(-(x-mu)**2/(2 * sig**2))

def fit_gauss(data):
    n=len(data)
    mu=data.mean()
    sigma=sum((data-mu)**2)/n
    #popt, pcov =  curve_fit(gaus_func,data,

def base_spectra(x, spread=80, offset=0):
    multi_gauss = np.zeros(len(x))
    mu = 96.5
    multi_gauss += gauss_func(x, spread, mu+offset)
    mu = 98.0
    multi_gauss += gauss_func(x, spread, mu+offset)
    return multi_gauss
 
print 'plotting sacla'
sacla_list = pd.read_csv("sacla_unit_cell.dat", sep=' ', index_col=0)
sacla_list['0']=sacla_list['0']*10
(mu, sigma) = norm.fit(sacla_list['0'])
print mu,sigma
n, bins, patches = plt.hist(sacla_list['0'], bins=500, range=(95.0,98.5))
y = mlab.normpdf( bins, mu, sigma)
l = plt.plot(bins, y, 'r--', linewidth=2)
plt.title('sacla_uc')
#plt.savefig('sacla_uc_test_gauss.png')
plt.show()
sys.exit()
print('reading I24 dose data')

file_list = pd.read_csv("/dls/i24/data/2018/nt14493-94/processing/scripts/new_stat_scripts/unit_cell_counter/pacman_unit_cells_all.dat", sep=' ', index_col=0)
print(file_list.columns)
file_list['file_number']=[value.strip('_')[1].strip('.')[0] for value in  file_list.index.values]
int_file_list = [file.split('.')[0].split('_')[-1] for file in file_list.index]
#print(int_file_list)
file_list['file_number']=int_file_list
#print(file_list)
dose_list=[int(value)%20+1 for value in file_list['file_number']]
cell_list=[float(value) for value in file_list['cell_type']]
file_list['dose']=dose_list

#plt.show()
for dose in range(1,21):
    print('Plotting dose %i'%dose)
    dose_df=file_list[file_list['dose']==dose]
    plt.hist(dose_df['cell_type'], bins=500, range=(95.0,98.5))
    plt.title('dose %i'%dose)
    plt.savefig('uc_by_dose_%i_3.png'%dose)
    #plt.show()




#plt.scatter(dose_list,cell_list)
#plt.savefig('all_uc.png')

