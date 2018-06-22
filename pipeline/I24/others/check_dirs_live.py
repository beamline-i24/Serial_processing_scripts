import os, glob
import sched, time
import pickle

def write_to_file(sc):
    print 'in write'
    f = open('spy-13Sept2017.txt','a')
    path='/dls/i24/data/2017/nt14493-78/' 
    list_of_folders = []
    num_per_file_dict = {} 
    for dir in glob.glob(path+ '/*/'):
        #print 'dir', dir, time.time() - os.path.getctime(dir)
        if (time.time() - os.path.getctime(dir)) > (10*6000):
            continue
        elif 'test' in dir or 'tmp' in dir or 'jpegs' in dir or 'process' in dir:
            continue
        else:
            for subdir in glob.glob(dir+'/*/'):
                #print '\tsubdir', subdir
                list_of_folders.append(subdir)

    #print list_of_folders

    for folder in sorted(list_of_folders):
        print folder, 
	try:
            fid_list = os.listdir(folder)
            truth_list = [True for file in fid_list[:100] if file.endswith('cbf')]
            if truth_list.count(True) < 1:
                continue
            line = '%s %s %s\n' %(time.time(), folder, len(fid_list))
            f.write(line)
            print '# of cbfs:', len(fid_list)
            num_per_file_dict[folder] = len(fid_list)
        except StandardError:
	    continue
    f.close()
    pickle.dump(num_per_file_dict, open('num_per_file_dict.pickle','w'))
    #s.enter(4, 5, write_to_file, (sc,))

def main():
    print 'Running'
    s = sched.scheduler(time.time, time.sleep)
    try:
        while True:
            s.enter(10, 10, write_to_file, (s,))
            s.run()
    except KeyboardInterrupt:
        return 0

if  __name__ == '__main__':
    x = main()
    print x
print 'EOP'
