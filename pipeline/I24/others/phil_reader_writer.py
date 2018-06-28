# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 17:03:11 2017

@author: web66492
"""

from libtbx.phil import parse
from dials.util.options import OptionParser, ConfigWriter
import libtbx.load_env
from cctbx.uctbx import unit_cell as uc
from cctbx.sgtbx import space_group_info as sgi

help_message = '''
DIALS script for processing still images. Import, index, refine, and integrate are all done for each image
seperately.
'''

control_phil_str = '''
  verbosity = 1
    .type = int(value_min=0)
    .help = "The verbosity level"
  dispatch {
    pre_import = False
      .type = bool
      .expert_level = 2
      .help = If True, before processing import all the data. Needed only if processing \
              multiple multi-image files at once (not a recommended use case)
    refine = False
      .expert_level = 2
      .type = bool
      .help = If True, after indexing, refine the experimental models
    squash_errors = True
      .expert_level = 2
      .type = bool
      .help = If True, if an image fails to process, continue to the next image. \
              otherwise, halt processing and show the error.
  }
  output {
    output_dir = .
      .type = str
      .help = Directory output files will be placed
    composite_output = False
      .type = bool
      .help = If True, save one set of json/pickle files per process, where each is a \
              concatenated list of all the successful events examined by that process. \
              If False, output a separate json/pickle file per image (generates a \
              lot of files).
    logging_dir = None
      .type = str
      .help = Directory output log files will be placed
    datablock_filename = %s_datablock.json
      .type = str
      .help = The filename for output datablock
    strong_filename = %s_strong.pickle
      .type = str
      .help = The filename for strong reflections from spot finder output.
    indexed_filename = %s_indexed.pickle
      .type = str
      .help = The filename for indexed reflections.
    refined_experiments_filename = %s_refined_experiments.json
      .type = str
      .help = The filename for saving refined experimental models
    integrated_filename = %s_integrated.pickle
      .type = str
      .help = The filename for final integrated reflections.
    integrated_experiments_filename = %s_integrated_experiments.json
      .type = str
      .help = The filename for saving final experimental models.
    profile_filename = None
      .type = str
      .help = The filename for output reflection profile parameters
    integration_pickle = int-%d-%s.pickle
      .type = str
      .help = Filename for cctbx.xfel-style integration pickle files
  }
  mp {
    method = *multiprocessing sge lsf pbs mpi
      .type = choice
      .help = "The multiprocessing method to use"
    nproc = 1
      .type = int(value_min=1)
      .help = "The number of processes to use."
  }
'''

dials_phil_str = '''
  input {
    reference_geometry = None
      .type = str
      .help = Provide an experiments.json file with exactly one detector model. Data processing will use \
              that geometry instead of the geometry found in the image headers.
  }
  output {
    shoeboxes = True
      .type = bool
      .help = Save the raw pixel values inside the reflection shoeboxes during spotfinding.
  }
  include scope dials.util.options.geometry_phil_scope
  include scope dials.algorithms.spot_finding.factory.phil_scope
  include scope dials.algorithms.indexing.indexer.index_only_phil_scope
  include scope dials.algorithms.refinement.refiner.phil_scope
  include scope dials.algorithms.integration.integrator.phil_scope
  include scope dials.algorithms.profile_model.factory.phil_scope
  include scope dials.algorithms.spot_prediction.reflection_predictor.phil_scope
  include scope dials.algorithms.integration.stills_significance_filter.phil_scope
  indexing {
    stills {
      method_list = None
        .type = strings
        .help = List of indexing methods. If indexing fails with first method, indexing will be \
                attempted with the next, and so forth
    }
  }
  integration {
    include scope dials.algorithms.integration.kapton_correction.absorption_phil_scope
  }
'''

program_defaults_phil_str = '''
indexing {
  method = fft1d
}
refinement {
  parameterisation {
    auto_reduction {
      min_nref_per_parameter = 1
      action = fix
    }
    beam.fix = all
    detector.fix = all
  }
  reflections {
    weighting_strategy.override = stills
    outlier.algorithm = null
  }
}
integration {
  integrator = stills
  profile.fitting = False
  background {
    algorithm = simple
    simple {
      outlier.algorithm = plane
      model.algorithm = linear2d
    }
  }
}
profile.gaussian_rs.min_spots.overall = 0
'''

phil_scope = parse(control_phil_str + dials_phil_str, process_includes=True).fetch(parse(program_defaults_phil_str))
usage = "usage: %s [options] [param.phil] filenames" % libtbx.env.dispatcher_name
parser = OptionParser(
      usage=usage,
      phil=phil_scope,
      epilog=help_message
      )
params, options, all_paths = parser.parse_args(show_diff_phil=False, return_unhandled=True)
#working_params = phil_scope.extract()
#working_params.verbosity=10
#diff_phil = parser.diff_phil.as_str()
#print(diff_phil)
params.verbosity=10
params.indexing.known_symmetry.unit_cell=uc(parameters=(78.3, 80.3, 96.3, 90, 90, 90))
params.indexing.known_symmetry.space_group=sgi(symbol='P212121')
params.indexing.basis_vector_combinations.max_refine=5
params.indexing.refinement_protocol.n_macro_cycles = 1
params.indexing.refinement_protocol.d_min_start = 2.5
params.indexing.multiple_lattice_search.max_lattices = 6
params.indexing.stills.indexer = 'Auto'
params.indexing.stills.refine_candidates_with_known_symmetry = True
params.indexing.stills.method_list = ["real_space_grid_search","fft1d"]
params.refinement.parameterisation.treat_single_image_as_still=True
print(params.integration.background.simple.outlier.algorithm)
params.integration.background.simple.outlier.algorithm = 'null'
params.significance_filter.enable = False
params.significance_filter.n_bins = 20
params.significance_filter.isigi_cutoff = 1
params.spotfinder.lookup.mask='/dls/i24/data/2017/nt14493-58/processing/stills_process/aldous/mask.pickle'
#params.spotfinder.filter.min_spot_size='Auto' #2
params.integration.lookup.mask='/dls/i24/data/2017/nt14493-63/processing/stills_process/aldous/mask.pickle'
#geometry {
#  detector {
#    panel {
#      fast_axis = 0.9999999881794411, 0.00012168850207415642, -9.398418122080865e-05
#      slow_axis = 0.00012142829505706178, -0.9999961736382771, -0.002763686663484808
#      origin = -217.60393606707456, 226.57961515668748, -268.4021547782846
#      }
#    }
#  }

modified_phil=phil_scope.format(python_object=params)
writer = ConfigWriter(phil_scope)
writer.write(params,'phil.phil')

#modified_phil.show()
#print(type(modified_phil),type(working_params))
#phil = open('modififed.phil','w')
#phil.write(modified_phil.as_str())
#for param in working_params:
#    phil.write(param)
#params, options, all_paths = parser.parse_args(show_diff_phil=True, return_unhandled=True)
#diff_phil = parser.diff_phil.as_str()
diff_phil = parser.diff_phil.as_str()
if diff_phil is not '':
      print('The following parameters have been modified:\n')
      print(diff_phil)
