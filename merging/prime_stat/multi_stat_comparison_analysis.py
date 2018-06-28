# -*- coding: utf-8 -*-
#!/dls_sw/apps/python/anaconda/1.7.0/64/bin/python
"""
Created on Mon Oct  9 11:43:24 2017

@author: web66492
"""

import pandas as pd
import numpy as np
from StringIO import StringIO
import matplotlib.pyplot as plt
import sys
import re
import os

# extract run_no
def get_file(log):
    file_name = open( log, "r" )
    return file_name.read()

def run_no(file_name):
    pattern = re.compile( r"run_no\s=\s(?P<dose>.*)", re.I )
    compile = pattern.search( file_name )
    doi = compile.group("dose")
    return doi

def ax2_values(ax2_ticks):
    x2 = ( 1/ ax2_ticks )/2
    return [ "%.2f" % z for z in x2 ]

# extract summary table of mean scaled merged mtz and convert to pandas table
def extract_mtz_table(log, run_num, file_name):
    file = open( log, "r" )
    table_str = ""
    for line in file:
        # skips intials line of input file:
        if line.strip() == "Summary for " + run_num + file_name:
            break
        # reads txt until the end of the block:
    for line in file:
        if line.strip() == "Summary of CC1/2 on three crystal axes":
            break
        table_str += line
    file.close()
    # convert string to pandas table
    table = StringIO( table_str )
    names = [ "bin", "top bin", "-", "bottom bin", "comp", "C obs", "/", "Cobs" ,"obs", "Rmerge", "Rsplit", "CC1/2", "N ind", "CCiso", "Nind", "CCanoma", "N_ind", "I/sigI", "I", "sigI", "I**2" ]
    usecols = [ "bin", "top bin", "bottom bin", "comp", "obs", "Rmerge", "Rsplit", "CC1/2", "I/sigI", "I", "sigI", "I**2" ]
    df = pd.read_csv( table ,
                      engine = "python" ,
                      header = None ,
                      names = names ,
                      skiprows = 2 ,
                      sep = "[*# ]+" ,
                      skipfooter = 4 ,
                      usecols = usecols ,
                      index_col = "bin" ,
                       )
    return df

def obs_table(dose, stat, mtz_table):
    # input mtz tables and define dataframes
    res = pd.DataFrame()
    mean_obs = pd.DataFrame()
    mtz_table_obs = pd.DataFrame()
    postref2_obs = pd.DataFrame()
    postref3_obs = pd.DataFrame()
    # extract obs columns
    res[ "res" ] = mtz_table[ "bottom bin" ]
    mtz_table_obs[dose] = mtz_table[stat]
    # create sin(theta)/lambda column
    res[ "1/2d" ] = res.apply( lambda x : 1/(2*x[ "res" ]), axis = 1  )
    # append resolution, mean, postref1, postref2 and postref3 obs columns
    frames = [ res ,
               mtz_table_obs]
    df = pd.concat( frames, axis=1 )
    df = df.drop( "res", 1 )
    df = df.set_index( "1/2d" )
    return df

def plt_figure(mtz_tables, stat, xtype, label):
    # input data frames
    names = sorted(mtz_tables.keys())
    fig=plt.figure()
    ax_sub = fig.add_subplot(111)
    colors = ['g','b','y','c','r','k', 'm']
    styles = ['-','-.','-x']
    for table_name in names:
	name =table_name.split('_')[1]
	img_num = table_name.split('_')[0]
	if int(img_num) == 1000:
	    i = 5
	    continue
	elif int(img_num) == 2000:
	    i = 1
	    continue
	elif int(img_num) == 4000:
	    i = 2
	    continue
	elif int(img_num) == 8000:
	    i = 3
	    continue
	elif int(img_num) == 12000:
	    i = 4
	    continue
	elif int(img_num) == 20000:
	    i = 6
	    if name.endswith('mean'):
		i=1
	    elif name.endswith('1'):
		i=2
	    elif name.endswith('2'):
		i=3
	else: 
	    i = 0
	    continue
	if name.endswith('jr'):
	   j = 1
	elif name.endswith('ref'):
	   j=2
	else:
	   j=0
	print table_name, i, j
	name =table_name.split('_')[1]
	img_num = table_name.split('_')[0]
        obs = obs_table(img_num, stat, mtz_tables[table_name])
        ax_sub.plot( obs,colors[i]+styles[j], label=name+' '+img_num)
        # set ax2 gridlines and values
        ax2_ticks = np.array( [ 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275 ] )
        ax_sub.set_xticks( ax2_ticks, minor=True )
        ax_sub.xaxis.grid( True, which="minor" )
        #ax_sub.set_xticklabels([])
	if xtype == 'resolution':
            ax_sub.set_xticks( ax2_ticks )
            ax_sub.set_xticklabels( ax2_values(ax2_ticks) )
            ax_sub.set_xlabel( r"resolution ($\AA$)" )
            ax_sub.set_ylabel(label )
            #ax_sub.set_ylim(0)
	elif xtype == 'sin':    
            ax_sub.set_xlabel( r"sin$\Theta/\lambda$ ($\AA^{-1}$)" )
            ax_sub.set_ylabel(label)
           # ax_sub.set_ylim(0)
        else:
	   print "unknown xtype", xtype
    ax_sub.legend(loc= "best", ncol=3)

def plt_figures(mtz_tables, stats):
    # input data frames
    names = mtz_tables.keys()
    print names
    fig = plt.figure()
    ax_sub_1 = fig.add_subplot(231)
    ax_sub_2 = fig.add_subplot(232)
    ax_sub_3 = fig.add_subplot(233)
    ax_sub_4 = fig.add_subplot(234)
    ax_sub_5 = fig.add_subplot(235)
    ax_sub_6 = fig.add_subplot(236)
    for table_name in names:
        dose=table_name.split('/')[-3]
        obs = obs_table(dose, 'obs', mtz_tables[table_name])
        rmerge = obs_table(dose, 'Rmerge', mtz_tables[table_name])
        rsplit = obs_table(dose, 'Rsplit', mtz_tables[table_name])
        CC = obs_table(dose, 'CC1/2', mtz_tables[table_name])
        IsigI = obs_table(dose, 'I/sigI', mtz_tables[table_name])
        I2 = obs_table(dose, 'I**2', mtz_tables[table_name])
	################ 1st subplot - obs ###################
        ax2 = ax_sub_1.twiny() # allows for 2nd x-axis
        ax_sub_1.plot( obs,label=dose)
        ax2.set_xlim(ax_sub_1.get_xlim())
        # set ax2 gridlines and values
        ax2_ticks = np.array( [ 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275 ] )
        # function to return ax2 values
        ax_sub_1.set_xticks( ax2_ticks, minor=True )
        ax_sub_1.xaxis.grid( True, which="minor" )
        ax_sub_1.set_xticklabels([])
        ax2.set_xticks( ax2_ticks )
        ax2.set_xticklabels( ax2_values(ax2_ticks) )
        ax2.set_xlabel( r"resolution ($\AA$)" )
        ax_sub_1.set_ylabel( "no. of observations" )
        ax_sub_1.set_ylim(0)
   	################ 2nd subplot - rmerge ###################
        ax2 = ax_sub_2.twiny() # allows for 2nd x-axis
        ax_sub_2.plot( rmerge, label=dose)
        ax2.set_xlim(ax_sub_2.get_xlim())
        # set ax2 gridlines and values
        ax2_ticks = np.array( [ 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275 ] )
        ax_sub_2.set_xticks( ax2_ticks, minor=True )
        ax_sub_2.xaxis.grid( True, which="minor" )
        ax_sub_2.set_xticklabels([])
        ax2.set_xticks( ax2_ticks )
        ax2.set_xticklabels( ax2_values(ax2_ticks) )
        ax2.set_xlabel( r"resolution ($\AA$)" )
        ax_sub_2.set_ylabel( r"R$_{merge}$" )
        ax_sub_2.set_ylim(0)
	################ 3rd subplot - rplit ###################
        ax2 = ax_sub_3.twiny() # allows for 2nd x-axis
        ax_sub_3.plot( rsplit, label=dose )
        ax2.set_xlim(ax_sub_3.get_xlim())
        # set ax2 gridlines and values
        ax2_ticks = np.array( [ 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275 ] )
        ax_sub_3.set_xticks( ax2_ticks, minor=True )
        ax_sub_3.xaxis.grid( True, which="minor" )
        ax_sub_3.set_xticklabels([])
        ax2.set_xticks( ax2_ticks )
        ax2.set_xticklabels( ax2_values(ax2_ticks) )
        ax2.set_xlabel( r"resolution ($\AA$)" )
        ax_sub_3.set_ylabel( r"R$_{split}$" )
        ax_sub_3.set_ylim(0)
	################ 4rd subplot - CC ###################
        ax2 = ax_sub_4.twiny() # allows for 2nd x-axis
        ax_sub_4.plot( CC, label=dose )
        ax2.set_xlim(ax_sub_4.get_xlim())
        # set ax2 gridlines and values
        ax2_ticks = np.array( [ 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275 ] )
        ax_sub_4.set_xticks( ax2_ticks, minor=True )
        ax_sub_4.xaxis.grid( True, which="minor" )
        ax2.set_xticklabels( [] )
        ax_sub_4.set_xlabel( r"sin$\Theta/\lambda$ ($\AA^{-1}$)" )
        ax_sub_4.set_ylabel( r"CC 1/2" )
        ax_sub_4.set_ylim(0)
	################ 5th subplot - I/sigI ###################
        ax2 = ax_sub_5.twiny() # allows for 2nd x-axis
        ax_sub_5.plot( IsigI,label=dose)
        ax2.set_xlim(ax_sub_5.get_xlim())
        # set ax2 gridlines and values
        ax2_ticks = np.array( [ 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275 ] )
        ax_sub_5.set_xticks( ax2_ticks, minor=True )
        ax_sub_5.xaxis.grid( True, which="minor" )
        ax2.set_xticklabels( [] )
        ax_sub_5.set_xlabel( r"sin$\Theta/\lambda$ ($\AA^{-1}$)" )
        ax_sub_5.set_ylabel( r"I/sig(I)" )
        ax_sub_5.set_ylim(0)
    	################ 6th subplot - I**2 ###################
        ax2 = ax_sub_6.twiny() # allows for 2nd x-axis
        ax_sub_6.plot( I2,label=dose)
        ax2.set_xlim(ax_sub_6.get_xlim())
        # set ax2 gridlines and values
        ax2_ticks = np.array( [ 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275 ] )
        ax_sub_6.set_xticks( ax2_ticks, minor=True )
        ax_sub_6.xaxis.grid( True, which="minor" )
        ax2.set_xticklabels( [] )
        ax_sub_6.set_xlabel( r"sin$\Theta/\lambda$ ($\AA^{-1}$)" )
        ax_sub_6.set_ylabel( r"I**2" )
        ax_sub_6.set_ylim(0)

    ax_sub_1.legend(loc= "best")
    ax_sub_2.legend(loc= "best")
    ax_sub_3.legend(loc= "best")
    ax_sub_4.legend(loc= "best")
    ax_sub_5.legend(loc= "best")
    ax_sub_6.legend(loc= "best")
    
def main():#log):
    paths = []
    paths.append('/dls/i24/data/2017/nt14493-63/processing/jhb/cunir/merlin_jr_ref/merged')
   # paths.append('/dls/i24/data/2017/nt14493-63/processing/jhb/cunir/merlin_jr/merged')
   # paths.append('/dls/i24/data/2017/nt14493-63/processing/jhb/cunir/waylin/merged')
    mtz_tables = {}
    stats = {}
    for dir_path in paths:
       for root, dirs, files in os.walk(dir_path):
        #check for dirs in dir_path of set format
        #loop through files in those dirs
         for dir in dirs:
           # if dir.endswith('3_1.75A'):
           path = os.path.join(root, dir)
           for file in os.listdir(path):
               if file == 'log.txt':
                   log = os.path.join(path, file)
                   print('log', log)
                   run_num=run_no(get_file(log))
                   print run_num
                   mean = extract_mtz_table(log, run_num, "/mean_scaled_merge.mtz")
                   postref1 = extract_mtz_table(log, run_num, "/postref_cycle_1_merge.mtz")
                   postref2 = extract_mtz_table(log, run_num, "/postref_cycle_2_merge.mtz")
                   postref3 = extract_mtz_table(log, run_num, "/postref_cycle_3_merge.mtz")
		   table_name =  log.split('/')[-3]
                  # mtz_tables[table_name+'_mean'] = mean
                  # mtz_tables[table_name+'_pf1'] = postref1
                  # mtz_tables[table_name+'_pf2'] = postref2
                   mtz_tables[table_name] = postref3
		   postref3.to_csv(table_name+'.csv')
    print mtz_tables
    plt_figure(mtz_tables, stat='obs',xtype='resolution', label="no. of observations" )
    plt_figure(mtz_tables, stat='Rmerge',xtype='resolution', label=r"R$_{merge}$" )
    plt_figure(mtz_tables, stat='Rsplit',xtype='resolution', label=r"R$_{split}$" )
    plt_figure(mtz_tables, stat='CC1/2',xtype='sin', label=r"CC 1/2" )
    plt_figure(mtz_tables, stat='I/sigI',xtype='sin',label=r"I/sig(I)" )
    plt_figure(mtz_tables, stat='I**2',xtype='sin', label=r"I**2" )
    plt.show() 

if __name__ == '__main__':
    main()#dir_path=sys.argv[1])
    
#plt.close()

