import reflections as ref
import argparse
import os
import re
import vmxi_finder_2 as vr
import datablock_splitter as ds
import strong_split as ss

def argparser(argv=None):
    parser = argparse.ArgumentParser(description = 'Hit Finder\n\
	                                 Analyses spot count data to produce an estimate\
	                                 of the hit rate for a given directory.\n\
	                                 EXAMPLE\n ./hit_finder.py')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument("-i" ,"--input_file", type=str, required=True)
    requiredNamed.add_argument("-n" ,"--nxs_file", type=str, required=True)
    requiredNamed.add_argument("-o" ,"--output_file", type=str, required=True)
    parser.add_argument("-c" ,"--spot_count_cutoff", type=int, default=30)
    parser.add_argument("-s" ,"--show_fig", type=bool, default=False)
    parser.add_argument("-cl" ,"--cluster", type=bool, default=False)
    args = parser.parse_args()
    return args

def main(args):
   log=args.input_file
   cluster=args.cluster
   output_file = args.output_file
   directory='.'
   output=re.compile(r'\| image \| \#spots \| \#spots_no_ice \| total_intensity \|')
   end=re.compile(r'\-+')
   out_file=open(output_file,'w')
   print 'converting log file'
   with open(log,'r') as log_file:
        for line in log_file:
           line_search=line
           x = output.search(line_search)
           if x:
              for i, line in enumerate(log_file):
                  line_check = line
                  end_check = end.search(line_check)
                  if i == 0:
                     continue
                  elif end_check:
                      break
                  blank, image, spots, no_ice, intensity, new_line = line_check.split('|')
                  out_file.write('<file-pattern-index>%04d</file-pattern-index> \n'%int(image)) 
                  out_file.write('<spot_count>%04d</spot_count> \n'%int(spots)) 
                  out_file.write('<spot_count_no_ice>%04d</spot_count_no_ice> \n'%int(no_ice)) 
                  out_file.write('<total_intensity>%04d</total_intensity> \n'%int(intensity)) 
              break
   out_file.close()
   print 'writing hits.dat'
   hits = vr.main(output_file, args.spot_count_cutoff, args.show_fig)
   file_name=log.split('.')[0]
   print 'converting json'
   print args.nxs_file, hits
   datablocks = ds.run([args.nxs_file], hits)
   print 'converting spots'
   strong = ss.run('%s.pickle'%(file_name), hits)
   #if strong > 0 and datablocks > 0:
   #   fil = open('directories.txt', 'a')
   #   fil.write('
   return 

if __name__ == '__main__':
   args=argparser()
   main(args)

