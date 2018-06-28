#!/dls_sw/apps/dials/dials-v1-6-4/build/bin/dials.python
import pickle
import sys
import numpy as np
import matplotlib.pyplot as plt
import nest as nst
import utils

def plot(dose_dicts, indicator, *args):
    fig = plt.figure(figsize=(9,6))
    ax = fig.add_subplot(111, axisbg='w')
    ax2 = ax.twinx() 
    l = []
    l2 = []
    for dose, dic in dose_dicts.items():
        v = dic[indicator]
        x = np.array(len(v)*[int(dose)-1])
        print x
        y = np.array(v)
        #ax.scatter(x, y, s=300, alpha='0.04')
        #ax.scatter(x+1, y, s=300, alpha='0.01', c='Grey')
        ax2.scatter(x+1, y, s=200, alpha='0.02', c='Grey')
        ax.bar(int(dose), len(x), align='center', color='k')
        #ax.errorbar(x, y, xerr=0.0, yerr=0.5)
        l.append(np.mean(y))
        l2.append(np.std(y))
        #l.append(np.median(r))
        #l.append(stats.mode(r)[0][0])
    ax2.plot(np.array([f for f in range(1,21)]), l, lw=2, c='darkgoldenrod')
    print dose_dicts.keys()
    print 'xxxxxxxxxxxxxxxxx', x, type(x), len(x)
    print 'yyyyyyyyyyyyyyyyy', l, type(l)
    #ax.errorbar(np.array([f for f in range(20)]), l, xerr=0.5, yerr=0.1, fmt='o', ecolor='g', capthick=50)
    #ax.errorbar(np.array([f for f in range(20)]), l, xerr=0.0, yerr=l2, fmt='o', color='k')
    ax.set_xticks([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])
    ax.set_xlim(0.5, 20.5)
    ax.set_ylim(0, 2000)
    ax.set_yticks([0,250,500])
    ax.set_ylabel('Number of Crystals                                                                        ')
    ax2.errorbar(np.array([f for f in range(1,21)]), l, xerr=0.0, yerr=l2, fmt='d', ecolor='k', color='dodgerblue', capsize=2, capthick=1)
    ax2.set_yticks([935000,940000,945000,950000,955000])
    ax2.set_ylabel('                                                                                   Volume')
    ax.set_xlabel('Dose')
    plt.title('Unit Cell Volume')
    plt.show()
    return 1

def main(*args):
    #path = '/dls/i24/data/2017/nt14493-63/processing/scripts/experiment_refinement_process_test_folder/waylinCD/'
    path = '/dls/i24/data/2018/nt14493-94/processing/stills_process/acnir/weezer123_jr/00000-32000/'
    chip_name = ''
    doses = 10
    indicator = 'stat_m'
    contiguous_limit = 1
    
    allowed_keyword_list = ['dir','chip_name','file','indicator','contiguous_limit','before_limit','doses', 'plimits']
    for arg in args:
        k = arg.split("=")[0]
        v = arg.split("=")[1]
        print "Keyword argument: %s=%s" % (k, v)
        there = [True for key in allowed_keyword_list if k in key]
        if True not in there:
            print 'Unknown arg in args:', arg
            print 'Allowed Keywords:', allowed_keyword_list
            print 'Exiting'
            return 0
        elif k == allowed_keyword_list[0]:
            path = v
        elif k == allowed_keyword_list[1]:
            chip_name = v
        elif k == allowed_keyword_list[4]:
            contiguous_limit = int(v)
        elif k == allowed_keyword_list[6]:
            doses = int(v)

    indicator_list = ['uc_vol', 'uc_len', 'stat_m', 'd_min', 'size']
    for arg in args:
        k = arg.split("=")[0]
        v = arg.split("=")[1]
        if 'indic' in k:
            if v in indicator_list:
                indicator = v
                print '\n\nYou have chosen to look at:', indicator
            else:
                print 'Unknown Indicator'
                print 'Indictator List', indicator_list
                return 0

    dose_dicts = {}
    for i in range(1, doses+1):
        dose_dicts[i] = {}
    for dose in dose_dicts.keys():
        for ind in indicator_list:
            dose_dicts[dose][ind] = []

    starts_list = nst.find_contiguous(chip_name=chip_name, doses=doses,
                                contiguous_limit=contiguous_limit, path=path)
    for c, start_num in enumerate(starts_list[:]):
        s = '%04d:%04d %02d%%  ' % (c, len(starts_list), 100*float(c)/len(starts_list))
        utils.print_flush(s)
        #print 'c', c, 'start_num', start_num
         
        for dose_num in range(doses):
            #print 'dose number', dose_num
            #fid = 'int-waylinCD0077_%05d_0.pickle' %(start_num + dose_num)
            fid = 'int-0-weezer0044_%05d.pickle' %(start_num + dose_num)
            #fid = 'int-0-battle0007_%06d.pickle' %(start_num + dose_num)
            #fid = 'int-0-fugees0013_%05d.pickle' %(start_num + dose_num)
            #fid = 'int-0-orlons0034_%05d.pickle' %(start_num + dose_num)
            #print fid
            try:
                jar = pickle.load(open(path + fid, 'r'))
            except StandardError, e:
                break
            obs = jar['observations'][0]
            uc_len = obs.unit_cell().parameters()[0]
            uc_vol = obs.unit_cell().volume()
            stat_m = obs.statistical_mean()
            d_min = obs.d_min()
            size = obs.size()
            dose_bin = dose_num+1
            if uc_len < 97.25:
                break
            dose_dicts[dose_bin]['uc_vol'].append(uc_vol)
            dose_dicts[dose_bin]['uc_len'].append(uc_len)
            dose_dicts[dose_bin]['stat_m'].append(stat_m)
            dose_dicts[dose_bin]['d_min'].append(d_min)
            dose_dicts[dose_bin]['size'].append(size)
    plot(dose_dicts, indicator, *args)
    #print dir(obs)
    print 'EOP'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print '\n\t\t\t\tPELICAN'
        print "\t\t\t\tEXAMPLE\n ./pelican.py dir=/dls/i24/data/2017/nt14493-63/ indicator=uc_vol \n"
        print "\t\t\t\tEXAMPLE\n ./pelican.py dir=/dls/i24/data/2017/nt14493-63/ indicator=stat_m \n"
        print '\t\t\t\tDOCUMENT\n https://docs.google.com/document/d/1osARU4TDkosdJZIhcILc7v_foH-4pCearg71k3Nrhg4/edit#heading=h.3n4jjttquv3z \n\n'
    else:
        main(*sys.argv[1:])

plt.close()
