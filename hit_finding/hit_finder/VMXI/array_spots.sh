module load dials/nightly
folder=$"synringe_03"
jet=$SGE_TASK_ID
mkdir pbp5
mkdir pbp5/$folder
mkdir pbp5/$folder/jet_$jet/
cd pbp5/$folder/jet_$jet
nxs=$"/dls/mx/data/cm19647/cm19647-2/xfel_20180518/pbp5/$folder/jet_experiment_$jet/jet_$jet.nxs"
echo $nxs
dials.import $(eval echo "/dls/mx/data/cm19647/cm19647-2/xfel_20180518/pbp5/$folder/jet_experiment_$jet/jet_$jet.nxs")
dials.find_spots datablock.json mp.nproc=20 per_image_statistics=True spotfinder.lookup.mask=/dls/mx/data/cm19647/cm19647-2/xfel_20180516/processing/syringe1/mask.pickle
mv strong.pickle $jet.pickle
mv datablock.json $jet.json
mv dials.find_spots.log $jet.log
$(eval echo "dials.python /dls/mx/data/cm19647/cm19647-2/xfel_20180516/processing/scripts/vmxi_writer.py -i $jet.log -n $nxs -o $jet.out -c 10 -cl True")
