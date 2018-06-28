# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 10:44:26 2017

@author: web66492
"""

import pandas as pd
import numpy as np
from iotbx.reflection_file_reader import any_reflection_file
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os


def read_mtz( file_path ):
    #READS IN MTZ FILES AND CONVERT THEM INTO ARRAYS
    intensities = None
    reader = any_reflection_file( file_path )
    assert reader.file_type() == "ccp4_mtz"
    arrays = reader.as_miller_arrays(merge_equivalents=False)
    for ma in arrays:
        if ma.info().labels == ['IOBS', 'SIGIOBS']:
            intensities = ma
        elif ma.info().labels == ['IOBS(+)', 'SIGIOBS(+)', 'IOBS(-)',
                                                             'SIGIOBS(-)']:
            intensities = ma
    assert intensities is not None
    intensities_1 = intensities.customized_copy(unit_cell=[96.40,96.40,
                                                           96.40,90,90,90])
    return intensities_1

def make_df( intensities, name ):
    #CREATES DATAFRAME WITH H,K,L,D_HKL AND I_DOSE# COLUMNS
    indice_names = [ "h", "k", "l" ]
    list_hkls = list(intensities.indices())
#    abs_hkl_array = np.abs(list_hkls)
    indices = pd.DataFrame(list_hkls,
                           columns=indice_names )
    d_hkl_names = [ "hkl", "d_hkl" ]
    d_hkl = pd.DataFrame ( list( intensities.d_spacings() ), 
                          columns=d_hkl_names )
    d_hkl.drop( d_hkl.columns[[0]], axis=1, inplace=True )
    data_names = ["%s"%(name)]
    sf = pd.DataFrame( columns=data_names )
    sf.iloc[:,0] = list( intensities.data() )
#    sf.iloc[:,1] = list( intensities.sigmas() )
    frames = [ indices ,
               d_hkl ,
               sf
              ]
    df = pd.concat( frames, axis=1 )
    return df
    
def make_table():
# make complete df of iobs + iobs-sigs from all 4 doses
#    dir_path = "/dls/i24/data/2017/nt14493-63/processing/merged/waylin/"
  #  dir_path = "/dls/i24/data/2017/nt14493-63/processing/scripts/martin/i24_toolkit"    
    #"/dls/i24/data/2017/cm16788-3/processing/jhb/hewl/br-auto-processed/"
    dir_path = "/dls/i24/data/2017/nt14493-63/processing/merged/merlin/merlin_JR_run5_ref_mtz/"
    path_names = []    
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file == 'postref_cycle_1_merge.mtz':
                 path_names.append(os.path.join(root, file))   
                 #"/dls/i24/data/2017/nt14493-63/processing/merged/waylin/dose1/waylin_dose1_1.5A/postref_cycle_1_merge.mtz" 
#    files_in_dir = os.listdir(dir_path)
    #file_names = [x for x in files_in_dir if x.endswith('waylin_dose1_1.5A/postref_cycle_1_merge.mtz"')]
    #path_names = ['%s%s'%(dir_path,x) for x in file_names]
    path_names.sort()
    intensities = [read_mtz(path) for path in path_names] #sfs2 = list(map(lambda x: read_mtz(x),paths))
    names = [path.split('/')[-2] for path in path_names]
    names.sort()
    assert len(intensities) == len(names)
    dfs = [make_df(intensity,
                   name) for intensity,name in zip(intensities,
                                                                names)]
#    df_final = reduce(lambda left,right: pd.merge(left,
#                                                  right, how = "outer",
#                                                  on=[ "h", "k", "l",
#                                                      "d_hkl" ]
#                                                      ),
#                                                      dfs)
    df_final = dfs[0]
    return df_final

def randomise_hkls(df):
    x = [str(h) + ' ' +str(k) + ' ' + str(l) for h,k,l in zip(df['h'],df['k'],df['l'])]
    df['x']=x
    df=df.set_index(df['x'])
    df2=df.copy()
    for x, x_new in zip(df2.index,np.random.permutation(df.index)):
        print x, x_new
        df2.loc[x]=df.loc[x_new]
        print 'new df2 %s: \n '%x, df2.loc[x], ' =  df %s: \n'%x_new, df.loc[x_new]
        print 'old', df.loc[x]
    return df2

df = make_table()
df2=randomise_hkls(df)
