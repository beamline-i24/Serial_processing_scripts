import os
import cctbx
import re
import pickle
import csv
import matplotlib.pyplot as plt

dir = "/dls/i24/data/2018/nt14493-94/processing/stills_process/acnir/weezer123_jr/stills_test/big_01"
listdir = os.listdir(dir)
#experiments_json_list = [file for file in listdir if file.endswith("refined_experiments.json"]
int_file_list = [file for file in listdir if file.startswith("int")]
#def detector_uc_finder(filename):
#    pattern = re.compile( r"run_no\s=\s(?P<dose>.*)", re.I )
#    compile = pattern.search( file_name )
#    doi = compile.group("dose")
#    return doi
det0 = []
det1 = []
det2 = []
unit0 = []
unit1 = []
unit2 = []
for file in int_file_list[:30000]:
      if int(file.split('.')[0].split('_')[-1])%100 == 0:
         print(file)
      jar = pickle.load(open(os.path.join(dir,file),'r'))
      d=jar['distance']
      uc=jar['observations'][0].unit_cell()
      #unita.append(uc.parameters()[0])	 
      #unitb.append(uc.parameters()[1])
      if file.startswith('int-0'):
      	unit0.append(uc.parameters()[0])
	det0.append(d)
      elif file.startswith('int-1'):
        unit1.append(uc.parameters()[0])
        det1.append(d)
      elif file.startswith('int-2'):
        unit2.append(uc.parameters()[0])
        det2.append(d)
with open('det_vs_uc_all_1.csv','w') as csvfile:
     writer = csv.writer(csvfile)
     writer.writerow(det0)
     writer.writerow(det1)
     writer.writerow(det2)
     writer.writerow(unit0)
     writer.writerow(unit1)
     writer.writerow(unit2)
plt.scatter(det2, unit2, c='b')
plt.scatter(det1, unit1, c='k')
plt.scatter(det0, unit0, c='g')
plt.legend()
plt.show()
