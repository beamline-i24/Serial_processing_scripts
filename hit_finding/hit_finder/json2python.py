import json
import os
import glob
import sys
import matplotlib.pyplot as plt
import numpy as np

from dials.util.options import flatten_reflections
from dials.util.phil import ReflectionTableConverters

converter = ReflectionTableConverters()

def sum_list(reflections):
     length_list= [len(rlist) for rlist in reflections]
     return float(sum(length_list))

def get_num_reflections(directory, file_name):
    strong_reflections=flatten_reflections(get_reflection_list(directory, file_name))
    strong_val=sum_list(strong_reflections)
    return float(strong_val)

def get_reflection_list(directory, file_name):
    reflection_list=[]
    reflection_list.append(converter.from_string(os.path.join(directory,file_name)))
    return reflection_list


def print_flush(string):
     sys.stdout.write('\r%s' % string)
     sys.stdout.flush()


def get_file_names(directory, current_image):
    current_image=int(current_image)
    int_0 = glob.glob(os.path.join(directory,"int-0*%05d*"%current_image))
    int_1 = glob.glob(os.path.join(directory,"int-1*%05d*"%current_image))
    int_2 = glob.glob(os.path.join(directory,"int-2*%05d*"%current_image))
    return int_0, int_1, int_2

def int_search(current_image, ints):
    img = "%05d"%int(current_image)
    ints=[int_fil for int_fil in ints if img in int_fil]
    int_0 = [int_0 for int_0 in ints if int_0.startswith('int-0')]
    int_1 = [int_1 for int_1 in ints if int_1.startswith('int-1')]
    int_2 = [int_2 for int_2 in ints if int_2.startswith('int-2')]
    if int_0:
       if int_1:
         if int_2:
            hit=3
         else: 
            hit=2
       else:
            hit=1
    else:
       hit=0
    return hit

def indx_search(current_image, ints, directory):
    img = "%05d"%int(current_image)
    indx=[int_fil for int_fil in ints if img in int_fil]
    if indx:
       return get_num_reflections(directory, indx[0])
    else:
       return None

with open('hanson.json') as f:
    data = json.load(f)

failed_but_indexed=0
fail = []
int_no_index=0
no_idx = []
miss_miss = 0
hit_hit = 0
directory ='/dls/i24/data/2018/nt14493-94/processing/stills_process/acnir/hanson_jr' 
dir_list= os.listdir(directory)
ints= [int_fil for int_fil in dir_list if int_fil.startswith('int')]
indxs= [indx_fil for indx_fil in dir_list if indx_fil.endswith('indexed.pickle')]
out_array=[]
for i, record in enumerate(data):
    print_flush(str(i))
    strong=record['n_spots_total']
    intensity=record['total_intensity']
    if float(record['total_intensity']) <= 0 or int(record['n_spots_no_ice']) <= 0:
       ratio=0
    else:
       ratio=(float(record['total_intensity'])/float(record['n_spots_no_ice']))
    hit = int_search(record['image'].split('_')[1].split('.')[0], ints)
    n_indexed = indx_search(record['image'].split('_')[1].split('.')[0], indxs, directory)
    noise_1 = record['noisiness_method_1']
    noise_2 = record['noisiness_method_2']
    #try:
    #   n_indexed=record['n_indexed']
    #   fraction_indexed=record['fraction_indexed']
    #except:
    #   n_indexed=0
    #   fraction_indexed=0
    if n_indexed:
       fraction_indexed=float(n_indexed)/strong
    else:
       fraction_indexed=0
    if hit == 0 and noise_1 > 0 and noise_1 < 0.875:
       #failed_but_indexed+=1
       fail.append(record['image'])
    if hit > 0 and noise_1 >= 0.875:
       #int_no_index+=1
       no_idx.append(record['image'])
    if hit == 0 and fraction_indexed == 0:
       miss_miss +=1
    if hit > 0 and fraction_indexed > 0:
       hit_hit +=1
    if strong > 16 and ratio > 20 and hit == 0:
       fail.append(record['image'])
    out_array.append([strong,intensity,ratio,hit,n_indexed,fraction_indexed, noise_1, noise_2, i])

print fail
print no_idx
with open('miss_low_noise.sh','w') as out:
     for image in fail:
         out.write('dials.stills_process %s acnir_2.phil \n'%image)
with open('hit_high_noise.sh','w') as out:
#     for image in fail:
#         out.write('dials.stills_process %s acnir_jr.phil \n'%image)
     for image in no_idx:
         out.write('dials.stills_process %s acnir_jr.phil \n'%image)
print 'failed to integrate but indexed:', failed_but_indexed
print 'failed to index in client but integrated:', int_no_index
print 'both miss:', miss_miss
print 'both_hit:', hit_hit
out_array=np.array(out_array)
strong = out_array[:,0]
intensity = out_array[:,1]
n_indexed = out_array[:,4]
fraction_indexed = out_array[:,5]
ratio=out_array[:,2]
hits = out_array[:,3]
image = out_array[:,8]
noise_1 = out_array[:,6]
noise_2 = out_array[:,7]
int_0_array = out_array[out_array[:,3] == 1]
int_1_array = out_array[out_array[:,3] == 2]
int_2_array = out_array[out_array[:,3] == 3]
miss_array = out_array[out_array[:,3] == 0]

print(len(image), len(noise_1))

plt.scatter(ratio,noise_1, c=hits, marker='o', label='noise_1')
plt.legend()
plt.colorbar()
plt.show()

plt.scatter(ratio,noise_2, c=hits, marker='o', label='noise_1')
plt.legend()
plt.colorbar()
plt.show()

plt.scatter(n_indexed, strong, c=fraction_indexed)
plt.colorbar()
plt.show()

plt.scatter(int_0_array[:,4], int_0_array[:,0], marker='o', c=int_0_array[:,5], label='int_0')
plt.scatter(int_1_array[:,4], int_1_array[:,0], marker='>', c=int_1_array[:,5], label='int_1')
plt.scatter(int_2_array[:,4], int_2_array[:,0], marker=(4,0), c=int_2_array[:,5], label='int_2')
plt.scatter(miss_array[:,4], miss_array[:,0],marker='+', c=miss_array[:,5], label='miss')
plt.legend()
plt.show()

#plt.scatter(intensity, strong, c=hits)
#plt.colorbar()
#plt.show()

plt.subplot(2,2,1)
plt.title('int_0')
plt.scatter(int_0_array[:,1], int_0_array[:,0], marker='o', c=int_0_array[:,5], label='int_0')
plt.colorbar()
plt.ylabel('strong_count')
plt.subplot(2,2,2)
plt.title('int_1')
plt.scatter(int_1_array[:,1], int_1_array[:,0], marker='>', c=int_1_array[:,5], label='int_1')
plt.colorbar()
plt.subplot(2,2,3)
plt.title('int_2')
plt.scatter(int_2_array[:,1], int_2_array[:,0], marker=(4,0), c=int_2_array[:,5], label='int_2')
plt.colorbar()
plt.ylabel('strong_count')
plt.xlabel('total_intensity')
plt.subplot(2,2,4)
plt.title('miss')
plt.scatter(miss_array[:,1], miss_array[:,0],marker=(6,0), c=miss_array[:,5], label='miss')
plt.colorbar()
plt.xlabel('total_intensity')
plt.show()

plt.subplot(2,2,1)
plt.scatter(strong, fraction_indexed, c=intensity)
plt.colorbar()
plt.subplot(2,2,2)
plt.scatter(intensity, fraction_indexed, c=strong)
plt.colorbar()
plt.subplot(2,2,3)
plt.scatter(ratio, fraction_indexed, c=hits)
plt.xlim(0, 1000)
plt.colorbar()
plt.subplot(2,2,4)
plt.show()

plt.scatter(ratio, strong, c=fraction_indexed)
plt.ylabel('strong_count')
plt.xlabel('ratio')
plt.colorbar()
plt.show()

plt.scatter(ratio, strong, c=hits)
plt.ylabel('strong_count')
plt.xlabel('ratio')
plt.colorbar()
plt.show()

plt.subplot(2,2,1)
plt.hist(int_0_array[:,2], bins = [0, 10, 50, 100, 150, 200, 300])
plt.subplot(2,2,2)
plt.hist(int_1_array[:,2], bins = [0, 10,  50, 100, 150, 200, 300])
plt.subplot(2,2,3)
plt.hist(int_2_array[:,2], bins = [0, 10, 50, 100, 150, 200, 300])
plt.xlabel('ratio')
plt.subplot(2,2,4)
plt.hist(miss_array[:,2], bins = [0, 10, 50, 100, 150, 200, 300])
plt.xlabel('ratio')
plt.show()
plt.hist(miss_array[:,1], bins = [0, 1000, 2000, 3000, 4000, 5000, 10000])
plt.xlabel('total_intensity')
plt.show()


