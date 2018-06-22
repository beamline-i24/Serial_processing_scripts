#file1=open('/dls/x02-1/data/2017/mx15722-8/processing/datasubsets/dhp-5bromo/5BI.pdb').readlines()
file1=open('/dls/x02-1/data/2017/mx15722-8/processing/datasubsets/dhp-5bromo/ligand_dir/5BI.pdb').readlines()
for i in file1:
   header=i.split()[0].upper()
   if (header=='ATOM' or header=='HETATM'):
     ligand_code=i[17:20].strip().upper()
     print ligand_code

