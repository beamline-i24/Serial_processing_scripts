# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 11:27:46 2017

@author: web66492
"""

import argparse
parser = argparse.ArgumentParser(description = 'GLOBAL_HAWK\n\
                                      Automatically run stills_process\
                                      on a given directory for a specific chip.\n\
                                      EXAMPLE\n ./global_hawk.py dir=/dls/i24/data/2017/nt14493-63/ p_name=CuNIR chip_name=waylinCD proctype=auto \n\
                                      \nFor more information see\
                                      DOCUMENT\n https://docs.google.com/document/d/1osARU4TDkosdJZIhcILc7v_foH-4pCearg71k3Nrhg4/edit#heading=h.3n4jjttquv3z')
parser.add_argument("visit_directory", type=str,
                    help="set visit directory e.g. /dls/ixx/data/xxxx/nt14493-63")
parser.add_argument("protein_name", type=str,
		    help="set protein name e.g. CuNIR")
parser.add_argument("chip_name",type=str,
		    help="set chip name e.g. waylin")
parser.add_argument("-p","--process_type", type=str,
		    help="set process type", default="stills", choices=['stills','manual'])
parser.add_argument("-o","--output_directory",type=str,
		    help="set output directory name if different from input naming convention")
parser.add_argument("-j","--job_limit", type=int,
		    help="number of jobs active at same time", default=20)
parser.add_argument("-i","--iteration_limit", type=int,
		    help="number of log iterations", default=1000)
parser.add_argument("-w","--wait_time", type=int,
		    help="log wait time before ending cycle", default=10)
parser.add_argument("-l","--log_name",type=str,
		    help="name of outputted log file", default='03102017_out.txt')
parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2],
                    help="increase output verbosity")
args = parser.parse_args()

print args.process_type
