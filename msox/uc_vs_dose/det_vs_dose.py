import os
import pandas as pd
import matplotlib.pyplot as plt
file_list = pd.read_csv("/dls/i24/data/2018/nt14493-94/processing/scripts/new_stat_scripts/unit_cell_counter/pacman_unit_cells_3.out", sep=' ', index_col=0)
print(file_list.columns)
int_file_list = [file.split('.')[0].split('_')[-1] for file in file_list.index]
#print(int_file_list)
file_list['file_number']=int_file_list
#print(file_list)
dose_list=[int(value)%20+1 for value in file_list['file_number']]
cell_list=[float(value) for value in file_list['cell_type']]
file_list['dose']=dose_list
print(file_list)

plt.scatter(dose_list,cell_list)
plt.savefig('all_uc.png')

