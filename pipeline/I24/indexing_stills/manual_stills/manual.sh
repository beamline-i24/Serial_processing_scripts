module load dials
for i in {1..6400}:
do
   i=$((i-1))
   printf -v initial_num "%05d" $i
   cbf="/dls/i24/data/2018/nt14493-94/pmfuta/clutch/clutch120009_$initial_num.cbf"
   identifier="clutch120009_$initial_num"
   datablock=$identifier+"_datablock.json"
   strong=$identifier+"_strong.pickle"
   experiments=$identifier+"_experiments.json"
   indexed=$identifier+"_indexed.pickle"
   integrated=$identifier+"_indexed.pickle"
   out="int_clutch120009_$initial_num.pickle"
   phil="/dls/i24/data/2018/nt14493-94/pmfuta/clutch/pmfuta.phil"
   dials.import $cbf output.datablock=$datablock $phil
   dials.spotfind $datablock output.reflections=$strong $phil
   dials.index $datablock $strong output.experiments=$experiments output.reflections=$indexed %phil
   dials.integrate $experiments $indexed output.reflections=$integrated $phil
   cxi.frame_extractor input.experiments=$experiments input.reflections=$integrated output.filename=$out 
done
