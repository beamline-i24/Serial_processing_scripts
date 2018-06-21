import os
import pandas as pd
import matplotlib.pyplot as plt
file_list = pd.read_csv("sacla_unit_cell.dat", sep=' ', index_col=0)#/dls/i24/data/2018/nt14493-94/processing/scripts/new_stat_scripts/unit_cell_counter/
file_list['0']=file_list['0']*10
plt.hist(file_list['0'], bins=500, range=(95.0,98.5))
plt.title('sacla_uc')
plt.savefig('sacla_uc.png')
    #plt.show()
#plt.scatter(dose_list,cell_list)
#plt.savefig('all_uc.png')

