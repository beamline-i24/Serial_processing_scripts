#!/usr/bin/python
#
#
#####################################################
#############  Run dials.stills forSFX data #########
#####################################################
#
# to run it
# python SFX_process.py file1 file2 
#
#
#######################################################
################### Modules section ###################
#######################################################
#
# Standard modules needed
import os,glob,sys,string,subprocess,shutil,stat

# Input from command line
li=sys.argv
file1 = os.path.abspath(li[1])
file2 = os.path.abspath(li[2])
# file1 is the list of files of nexus file to process
# file2 contains info such as SPG, unit cell paramereter

data=open(file2, 'r')
datacontents2 = data.readlines()
data.close()

# datacontents2[0] is SPG, [1] is unit cell and [2] refinement d_min


# Extra modules needed
#
#
#######################################################
################## Functions section ##################
#######################################################
#
# Merge types with files and/or keywords
def createCmdLine(pgram,typelist,filelist,logfile=None,cmdfile=None):

 cmdline = pgram
 for i in range(len(typelist)):
  cmdline = string.join([cmdline,typelist[i],filelist[i]])
 if cmdfile is not None:  
  cmdline = string.join([cmdline,"<",cmdfile])
 if logfile is not None:  
  cmdline = string.join([cmdline,">",logfile])

 return cmdline 
#
#
# split file name like "L_01_02_infl.mtz" into "01", "02", and "infl"
# field 3 = "infl", 2 = "02", 1 = "01" 
def splitname(filename, field):

 tmp = string.split(filename, sep=".")
 tmp2 = tmp[len(tmp)-2]
 tmp3 = string.split(tmp2,sep="_")
 if field == 1:
  tmp4 = tmp3[len(tmp3)-3]
 if field == 2:
  tmp4 = tmp3[len(tmp3)-2]
 if field == 3:
  tmp4 = tmp3[len(tmp3)-1] 
 if field >= 4: raise SystemExit("Problem in splitname function, field must 1 or 2")
 return tmp4

#
#
# found on internet: http://my.safaribooksonline.com/book/programming/python/0596001673/files/pythoncook-chp-4-sect-16
# to split directory path into a list
def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts

#
#######################################################
######################### Main ########################
#######################################################
#
# Read input file file1 
data=open(file1, 'r')
datacontents = data.readlines()
data.close()

for i in range(len(datacontents)):
	line = datacontents[i] 
	if line!='\n':
		stuff=string.split(line.strip('\n'), sep='/')
		working_dir=string.split(stuff[-1], sep='.')
		if os.path.exists(working_dir[0]): shutil.rmtree(working_dir[0])
		os.makedirs(working_dir[0])
		os.chdir(working_dir[0])
		shutil.copy2('/home/hqp77592/script/SFX_script/input.phil', '.')
		with open('input.phil', 'r') as file:
			filedata = file.read()
		filedata = filedata.replace('space_group =', datacontents2[0])
		filedata1 = filedata.replace('unit_cell =', datacontents2[1])
		filedata2 = filedata1.replace('spotfinder.lookup.mask=', datacontents2[2])
		filedata3 = filedata2.replace('integration.lookup.mask=', datacontents2[3])
                filedata4 = filedata3.replace('input.reference_geometry=', datacontents2[4])	
		with open('input.phil', 'w') as file:
			file.write(filedata4)
#		import_string=str("dials.import " + line)
		script=str(working_dir[0]+".sh")
		if os.path.exists(script): os.remove(script)	
		f=open(script, "a")
		f.write("module load dials\n")
#		f.write(import_string)
		f.write("dials.stills_process input.phil " +line)
		f.close()
		os.chmod(script , stat.S_IRUSR| stat.S_IWUSR | stat.S_IXUSR)
		subprocess.call(['module load global/cluster && qsub -cwd -pe smp 20 -q low.q '+script],shell=True)
		os.chdir("..")
	else : pass
