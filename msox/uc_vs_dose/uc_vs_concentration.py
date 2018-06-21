import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
directory='/dls/i24/data/2018/nt14493-94/processing/scripts/new_stat_scripts/unit_cell_counter/unit_cell_counter_script/paper_dats/'
directory_list=[x for x in os.listdir(directory) if x.endswith('.dat')]

for dat_file in sorted(directory_list):
    file_df = pd.read_csv(os.path.join(directory,dat_file), sep=' ', index_col=0)
    #print('Plotting dose %i'%dose)
    #dose_df=file_list[file_list['dose']==dose]
    ymin, ymax = 0, 180
    axes = plt.gca()
    axes.set_ylim([ymin,ymax])
    n, bins, patches = plt.hist(file_df['cell_type'], bins=50, range=(96.0,98.5))
    conc=dat_file.split('.')[0]
    plt.title('concentration %s'%conc)
    #plt.savefig('bender_uc_by_concentration_density_%s.png'%conc)
    plt.show()
#plt.scatter(dose_list,cell_list)
#plt.savefig('igy1234_all_uc.png')

