module load dials
folder=$"lysozyme_01"
jet=$"82"
mkdir $folder/$jet/
cd $folder/$jet
nxs=$/dls/mx/data/cm19647/cm19647-2/xfel_20180517/20180517/$folder/jet_experiment_$jet/jet_$jet.nxs
dials.import nxs
dials.find_spots datablock.json mp.nproc=20 per_image_statistics=True spotfinder.lookup.mask=/dls/mx/data/cm19647/cm19647-2/xfel_20180516/processing/syringe1/mask.pickle
mv strong.pickle $jet.pickle
mv datablock.json $jet.json
mv dials.find_spots.log $jet.log
$(eval echo "dials.python /dls/mx/data/cm19647/cm19647-2/xfel_20180516/processing/scripts/vmxi_writer.py -i $jet.log -n $nxs -o $jet.out -c 30 -cl True")
