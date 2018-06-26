#!/dls_sw/apps/dials/dials-v1-9-3/build/bin/dials.python
#

import argparse
from subprocess import call
from pprint import pprint
import uuid
import time
import os
import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.append('/dls_sw/i24/scripts/setup_beamline')
import pv,ca

import Queue
import workflows.recipe
from workflows.transport.stomp_transport import StompTransport

#import logging
#logging.basicConfig(level=logging.DEBUG)

def argparser():
    parser = argparse.ArgumentParser( description="blah")
    parser.add_argument( "-v", "--visit_directory", default = None,
                        help="visit directory e.g. /dls/i24/2018/xxxxxxx-xx" )
    parser.add_argument("-c", "--chip_name",
                        help ="chip name e.g. xxxxxx")
    parser.add_argument("-s", "--sub_directory",
                        help="sub_directory e.g. cunir")
    parser.add_argument("-r", "--run_number",
                        help="chip run number e.g. 0044, can be given as 44")
    parser.add_argument("-ps", "--pattern_start", default = None,
                        help="first image number e.g. 00000 can be given as 0")
    parser.add_argument("-pe", "--pattern_end", default = None,
                        help="last image number e.g. 25600 ")
    parser.add_argument("-o", "--output_directory", default = None,
                        help="first image p e.g. cunir")
    parser.add_argument("-m", "--mask", default = None,
                        help="full file path for diffraction pattern mask at specific detector distance e.g. mask.pickle")
    parser.add_argument("-sc","--spot_count_cutoff", type=int, default = 30,
			help="spot_count_threshold, default= 30")
    parser.add_argument("-dm","--d_min_cutoff", type=float, default = None,
			help="max resolution for image to be processed, default=cbf header resolution")
    parser.add_argument("-dx","--d_max_cutoff", type=float, default = None,
			help="max resolution for image to be processed, default=cbf header resolution")
    args = parser.parse_args()
    return args

def log_fit(x,y):
    print x,y
    a,b = np.polyfit(np.log(x),y,1, w=np.sqrt(y))
    return a*np.log(np.unique(x))+b

def get_run_number(input_directory):
    print 'fuck you danny'
    run_file = [fil for fil in os.listdir(input_directory) if fil.endswith('00000.cbf')]
    run_number = int(run_file[0].split(chip_name)[1].split('_')[0])
    return run_number

def print_flush(string):
    sys.stdout.write('\r%s' % string)
    sys.stdout.flush()

def output_directory_check(output_directory):
    print('checking for directory, output_directory')
    if os.path.isdir(output_directory):
       print('directory exists', output_directory)
    else:
       print('making directory,', output_directory)
       os.makedirs(output_directory)
       time.sleep(2)
    return output_directory

StompTransport.load_configuration_file('/dls_sw/apps/zocalo/secrets/credentials-i24.cfg')
# StompTransport.load_configuration_file('/dls_sw/apps/zocalo/secrets/credentials-live.cfg')

args=argparser()
output_directory = None
if args.visit_directory: 
   visit_directory = args.visit_directory
   sub_directory = args.sub_directory
   chip_name = args.chip_name
   input_directory = os.path.join(visit_directory, sub_directory)
   if args.run_number:
      run_number = int(args.run_number)
   else:
      run_file = [fil for fil in os.listdir(input_directory) if fil.endswith('00000.cbf')]
      run_number = int(run_file[0].strip(chip_name).strip('_00000.cbf'))
   pattern = os.path.join(input_directory, "%s%04d_"%(chip_name, run_number)+"%05d.cbf")
   out_string = chip_name
else:
   visit_directory = ca.cagetstring(pv.pilat_filepath)
   print visit_directory
   if visit_directory.startswith('/ramdisk'):
      visit_directory = visit_directory.replace('ramdisk','dls/i24/data')
      print 'visit_director', visit_directory
   run_number = int(ca.caget('BL24I-EA-PILAT-01:cam1:FileNumber'))-1
   filefromdet = ca.cagetstring('BL24I-EA-PILAT-01:cam1:FileName_RBV')
   out_string = filefromdet
   #pattern = os.path.join(visit_directory, "%s%04d_"%(filefromdet, run_number)+"%05d.cbf")
   pattern = os.path.join(visit_directory, "%s"%(filefromdet)+"%05d.cbf")
print pattern
parts = visit_directory.split('/')
#chip_name=parts[5]
#run=parts[6]
output_directory = os.path.join('/'+parts[0],parts[1],parts[2],parts[3],parts[4],parts[5], 'processing', 'image_analysis')
print '-------------', output_directory
token = output_directory_check(output_directory)

#pattern = "/dls/i24/data/2018/nt14493-104/had3/agouti/agouti0044_%05d.cbf"
#pattern = "/dls/i24/data/2018/mx19458-1/IPNS/syringe2/run6/IPNS2_%05d.cbf"
#chip_name = 'chip_name'
#sub_directory='image_analysis'
if args.pattern_start:
   pattern_start = int(args.pattern_start)
else:
   pattern_start = 1 #ca.caget(pv.pilat_numimages)
if args.pattern_end:
   pattern_end = int(args.pattern_end)
else:
   pattern_end =  ca.caget(pv.pilat_numimages+'_RBV')
#pattern_start = 0
timeout_first = 30
timeout = 30
results_seen = 0
spot_cutoff = args.spot_count_cutoff
d_min_cutoff = args.d_min_cutoff
d_max_cutoff = args.d_max_cutoff
out_array=[]
unique_processing_id = str(uuid.uuid4())
mask=args.mask #'/dls/i24/data/2018/nt14493-94/processing/stills_process/mask-310.pickle'

processing_recipe = \
{
  "1": { "service": "DLS file watcher",
         "queue": "filewatcher",
         "parameters": { "pattern": pattern,  
                         "pattern-start": pattern_start,
                         "pattern-end": pattern_end,
                         "burst-wait": 1,
                         "timeout-first": timeout_first, # seconds to wait for the first file to appear
                         "timeout": timeout, # seconds to wait for new files to appear
                       },
         "output": { "every": 2 }
       },
  "2": { "service": "DLS Per-Image-Analysis",
         "queue": "per_image_analysis",
         "output": 3,
         "parameters": { 'd_min': d_min_cutoff, 'd_max': d_max_cutoff  , 'spotfinder.lookup.mask':mask, 'json':chip_name+'.json'} 
       },
  "3": { "service": "Feedback for I24 serial crystallography",
         "queue": "transient.i24.pia_feedback",
         "parameters": { "id": unique_processing_id,
                       },
       },
  "start": [
     [1, []]
  ]
}

message = { 'custom_recipe': processing_recipe,
            'parameters': {},
            'recipes': [],
          }

stomp = StompTransport()
stomp.connect()
stomp.send(
    'processing_recipe',
     message
)

class Image:
    def __init__(self, spot_dict, out_file):
       #self.spot_dict = spot_dict
       #self.image_num = self.image_number()
       #self.res_min = self.resolution_min()
       #self.file_str = self.file_name()
       #self.strong_spots = self.spot_count()
       #self.total_intensity = self.intensity()
       #self.outfile = out_file
       self.write_file(spot_dict, out_file)
       #print(self.image_num)

    def image_number(self):
       file_pattern_index = self.spot_dict['file-pattern-index']
       return file_pattern_index

    def file_name(self):
       file_str = self.spot_dict['file'] #/dls/i24/data/2018/nt14493-94/acnir/angels120002_00169.cbf
       file_number = self.spot_dict['file-number']
       return file_str

    def resolution_min(self):
       d_min_distl_method_1 =self.spot_dict['d_min_distl_method_1']
       d_min_distl_method_2 =self.spot_dict['d_min_distl_method_2']
       estimated_d_min = self.spot_dict['estimated_d_min']
       return estimated_d_min

    def spot_count(self):
       n_spots_4A = self.spot_dict['n_spots_4A']
       n_spots_no_ice = self.spot_dict['n_spots_no_ice']
       n_spots_total = self.spot_dict['n_spots_total']
       return n_spots_total

    def noisiness(self):
       noisiness_method_1 = self.spot_dict['noisiness_method_1']
       noisiness_method_2 = self.spot_dict['noisiness_method_2']
       return noisiness_method_1

    def intensity(self):
       total_intensity = self.spot_dict ['total_intensity']
       return total_intensity

    def write_file(self, spot_dict, out_file):
        out_file.write('<Image>\n')
        out_file.write('<file>'+str(spot_dict['file']) + '</file>' +'\n')
        out_file.write('<file-pattern-index>'+str(spot_dict['file-pattern-index']) + '</file-pattern-index>' +'\n')
        out_file.write('<file-number>'+str(spot_dict['file-number']) + '</file-number>' +'\n')
        out_file.write('<spot_count_no_ice>'+str(spot_dict['n_spots_no_ice']) + '</spot_count_no_ice>' +'\n')
        out_file.write('<spot_count>'+str(spot_dict['n_spots_total']) + '</spot_count>' +'\n')
        out_file.write('<spot_count_4A>'+str(spot_dict['n_spots_4A']) + '</spot_count_4A>' +'\n')
        out_file.write('<d_min>'+str(spot_dict['estimated_d_min']) + '</d_min>' +'\n')
        out_file.write('<d_min_method_1>'+str(spot_dict['d_min_distl_method_1']) + '</d_min_method_1>' +'\n')
        out_file.write('<d_min_method_2>'+str(spot_dict['d_min_distl_method_2']) + '</d_min_method_2>' +'\n')
        out_file.write('<noise_1>'+str(spot_dict['noisiness_method_1']) + '</noise_1>' +'\n')
        out_file.write('<noise_2>'+str(spot_dict['noisiness_method_2']) + '</noise_2>' +'\n')
        out_file.write('<total_intensity>'+str(int(spot_dict['total_intensity'])) + '</total_intensity>' +'\n')
        out_file.write('</Image>\n')
        out_file.flush()
        return 

q=Queue.Queue()
def receiver(rw, header, message):
   if rw.recipe_step.get("parameters", {}).get("id") == unique_processing_id:
     q.put(message)

def plot(out_array, spot_cutoff, plot_log=True, show=True):
       np_array = np.array(out_array)
       plt.scatter(np_array[:,1],np_array[:,2])
       if plot_log:
           a,b = np.polyfit(np.log(np_array[:,1]),np_array[:,2],1, w=np.sqrt(np_array[:,2]))
           rate=0
           for num, i, strong in np_array:
               if i == 0.1 and strong == 0.1:
                  continue
               elif i == 0:
                  continue
               elif strong < spot_cutoff:
                  continue
               elif strong <= a*np.log(i)+b:
                  rate+=1
	   plt.plot(np.unique(np_array[:,1]), log_fit(np_array[:,1], np_array[:,2]), label=out_file)
       if show:
	    plt.show()
       else:
           plt.draw()
       print('rate = %f'%(float(rate)/len(np_array)))

print('starting per image analysis')
print('loading pattern: ', pattern)
print('images:', pattern_start, pattern_end)
print('spot_cutoff:', spot_cutoff)
print('min_resolution:', d_min_cutoff)
print('max_resolution:', d_max_cutoff)

pprint('initiating queue')

workflows.recipe.wrap_subscribe(stomp, 'transient.i24.pia_feedback', receiver, acknowledgement=False)

results = [ False ] * (int(pattern_end) - int(pattern_start))

print output_directory

#with open('%s.out'%(chip_name), 'w') as out_file:
with open(os.path.join(output_directory,'%s.out'%(out_string)), 'w') as out_file:
    print('file made')
    while True:
#   while not all(results) or not timeout:
       message = q.get()#timeout=60)
#      results[message["file-number"] - 1] = ...
       pprint(message)
       image = Image(message, out_file)
       results[message["file-number"] - 1] = message
       # #out_array.append([message['file-pattern-index'], message['total_intensity'],message['n_spots_no_ice']])
       results_seen += 1
       print(results_seen)
       if int(results_seen) >= (int(pattern_end)):
           break
       #if ca.caget(pv.me14e_gp9) != 0:
       #    print 50*' COLLECTION ABORTED '
       #    break
 
with open(os.path.join(output_directory,'%s.json'%(out_string)), 'wb') as out:
     json.dump(results, out)

print(results_seen , 'out of ', pattern_end, 'images processed')
#plot(out_array, spot_cutoff)

time.sleep(1)
stomp.disconnect()
