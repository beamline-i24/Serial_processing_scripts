#!/dls_sw/apps/dials/dials-v1-9-1/build/bin/dials.python


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

import logging
logging.basicConfig(level=logging.DEBUG)

StompTransport.load_configuration_file('/dls_sw/apps/zocalo/secrets/credentials-i24.cfg')
# StompTransport.load_configuration_file('/dls_sw/apps/zocalo/secrets/credentials-live.cfg')

visit_directory = ca.cagetstring(pv.pilat_filepath)
print visit_directory
if visit_directory.startswith('/ramdisk'):
    visit_directory = visit_directory.replace('ramdisk','dls/i24/data')
    print 'visit_director', visit_directory

filefromdet = ca.cagetstring('BL24I-EA-PILAT-01:cam1:FileName_RBV')
pattern = os.path.join(visit_directory, "%s"%(filefromdet)+"%04d.cbf")
print pattern

#pattern = "/dls/i24/data/2018/nt14493-104/had3/agouti/agouti0044_%05d.cbf"
#chip_name = 'chip_name'
#sub_directory='image_analysis'
pattern_start = 0
pattern_end =  2000
timeout_first = 0
timeout = 0
results_seen = 0
spot_cutoff = 15
d_min_cutoff = 1.63
out_array=[]
unique_processing_id = str(uuid.uuid4())


processing_recipe = \
{
  "1": { "service": "DLS file watcher",
         "queue": "filewatcher",
         "parameters": { "pattern": pattern,  
                         "pattern-start": pattern_start,
                         "pattern-end": pattern_end,
                         "timeout-first": timeout_first, # seconds to wait for the first file to appear
                         "timeout": timeout, # seconds to wait for new files to appear
                       },
         "output": { "every": 2 }
       },
  "2": { "service": "DLS Per-Image-Analysis",
         "queue": "per_image_analysis",
         "output": 3
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

def receiver(rw, header, message):
  if rw.recipe_step.get("parameters", {}).get("id") == unique_processing_id:
     q.put(message)

print('starting per image analysis')
print('loading pattern: ', pattern)
print('images:', pattern_start, pattern_end)
print('spot_cutoff:', spot_cutoff)
print('min_resolution:', d_min_cutoff)

pprint('initiating queue')

workflows.recipe.wrap_subscribe(stomp, 'transient.i24.pia_feedback', receiver, acknowledgement=False)

time.sleep(1)
stomp.disconnect()
