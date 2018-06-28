import os
import pandas as pd
import matplotlib.pyplot as plt
import sys

def find_concentration_number(name):
    concentration_number=int(name.split('_')[0].split('bender')[1].split('x')[0])
    print name
    if concentration_number == 1:
       concentration_number = 8
    elif concentration_number == 2:
       concentration_number = 4
    elif concentration_number == 4:
       concentration_number = 2
    elif concentration_number == 8:
       concentration_number = 1
    elif concentration_number == 10:
       concentration_number = 30
    elif concentration_number == 15:
       concentration_number = 20
    elif concentration_number == 20:
       concentration_number =  15
    elif concentration_number == 30:
       concentration_number = 10
    else:
        print concentration_number, 'BROKEBROKEBROKEBROKEBROKEBROKEBROKE'
        sys.exit()
    print concentration_number
    return concentration_number

file_list = pd.read_csv("/dls/i24/data/2018/nt14493-94/processing/scripts/new_stat_scripts/unit_cell_counter/unit_cell_counter_script/bender_dats/all.dat", sep=' ', index_col=0)
print(file_list.columns)
file_list['Dilution']=[find_concentration_number(value) for value in  file_list.index.values]
#nt_file_list = [file.split('.')[0].split('_')[-1] for file in file_list.index]
#print(int_file_list)
#ile_list['file_number']=int_file_list
#print(file_list)
#ose_list=[int(value)%20+1 for value in file_list['file_number']]
#ell_list=[float(value) for value in file_list['cell_type']]
#ile_list['dose']=dose_list
#rint(file_list)

file_list.to_csv('bender_uc_vs_conc_all.dat', sep=',')

#for dose in range(1,11):
    #print('Plotting dose %i'%dose)
    #dose_df=file_list[file_list['dose']==dose]
    #plt.hist(dose_df['cell_type'], bins=500, range=(96.0,98.5))
    #plt.title('dose %i'%dose)
    #plt.savefig('igy1234_uc_by_dose_%i.png'%dose)
    #plt.show()

#plt.scatter(dose_list,cell_list)
#plt.savefig('igy1234_all_uc.png')

