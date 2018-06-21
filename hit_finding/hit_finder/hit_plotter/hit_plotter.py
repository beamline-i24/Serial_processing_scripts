import matplotlib.pyplot as plt
import matplotlib
import matplotlib.colors as colors
import matplotlib.cm as cm

def plot_hist(data_list):
   plt.hist(data_list, bins=500)
   plt.show()
   return

def compare_hits_plot(np_array, compare=False):
    if compare:
       clist = list(np_array[:,2])
       minima, maxima = min(clist), max(clist)
       print minima, maxima
       hits=np_array[np_array[:,2]==1]
       total_hits=np_array[np_array[:,2]>=1]
       scatter = plt.scatter(np_array[:,3], np_array[:,1], c=clist, vmin=0, vmax=1, s=8, cmap=cm.winter)
       plt.ylim(ymin=0, ymax=max(hits[:,3]))
       plt.colorbar(scatter)
       plt.axhline(spot_count_cutoff)
    else:
       scatter = plt.scatter(np_array[:,3], np_array[:,1])


def pickle_ratio_plot(np_array):
    clist = list(np_array[:,5])
    minima, maxima = min(clist), max(clist)
    print minima, maxima
    scatter = plt.scatter(np_array[:,1], np_array[:,2], c=clist, s=8, cmap=cm.winter)
    plt.colorbar(scatter)
    plt.axhline(spot_count_cutoff)
