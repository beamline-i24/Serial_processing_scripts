from dxtbx.datablock import DataBlockFactory
from dxtbx.datablock import DataBlockDumper
import os
import sys

def do_import(filename):
  datablocks = DataBlockFactory.from_filenames([filename])
  if len(datablocks) == 0:
    try:
      datablocks = DataBlockFactory.from_json_file(filename)
    except ValueError:
      raise Abort("Could not load %s"%filename)

  if len(datablocks) == 0:
    raise Abort("Could not load %s"%filename)
  if len(datablocks) > 1:
    raise Abort("Got multiple datablocks from file %s"%filename)

  # Ensure the indexer and downstream applications treat this as set of stills
  reset_sets = []

  from dxtbx.imageset import ImageSetFactory
  for imageset in datablocks[0].extract_imagesets():
    image = ImageSetFactory.imageset_from_anyset(imageset)
    image.set_scan(None)
    image.set_goniometer(None)
    reset_sets.append(image)

  return DataBlockFactory.from_imageset(reset_sets)[0]

def run(all_paths, hits):
    print 'importing {}'.format(all_paths )
    datablocks = [do_import(path) for path in all_paths]
    split_datablocks = []
    print 'processing datablocks'
    counter = 0
    for datablock in datablocks:
      for imageset in datablock.extract_imagesets():
        paths = imageset.paths()
        for i in xrange(len(imageset)):
          print i
          subset = imageset[i:i+1]
          split_datablocks.append(DataBlockFactory.from_imageset(subset)[0])
          if i in hits:
             counter += 1
             print(paths[i])
             dump = DataBlockDumper(split_datablocks[i])
             dump.as_json('datablock_%i.json'%i)
    return counter

if __name__ == '__main__':
   run(sys.argv[1:])
