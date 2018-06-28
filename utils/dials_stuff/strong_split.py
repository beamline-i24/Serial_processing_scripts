from libtbx import easy_pickle
from dials.array_family import flex
import sys

def run(input_file, hits):
    print 'opening {}'.format(input_file)
    strong = easy_pickle.load(input_file)
    z = strong['xyzobs.px.value'].parts()[2]
    print 'processing strong.pickles'
    counter = 0
    for i in xrange(int(flex.max(z))):
      print i
      if i in hits:
         subset = strong.select((z >= i) & (z < i+1))
         if len(subset) == 0: continue
         subset.as_pickle("strong_%d.pickle"%i)
         counter += 1
    return counter

if __name__ == '__main__':
   run(sys.argv[1:])
