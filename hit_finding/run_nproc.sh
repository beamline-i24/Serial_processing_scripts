module load dials/nightly

initial_num=$((SGE_TASK_ID-1))
printf -v i "%d" $initial_num 
# start the server in the background
nohup dials.find_spots_server nproc=20 > dials.server.out 2> dials.server.err < /dev/null &

# give server time to start
sleep 5

sub_dir=dtpaa
chip_name=pmoney
#i=7
run_num=0027
files=$(eval echo "/dls/i24/data/2018/nt14493-94/${sub_dir}/${chip_name}/*.cbf")

time dials.find_spots_client \
  d_min=1.8 d_max=40 \
  json=${chip_name}.json \
  refinement_protocol.n_macro_cycles=1 \
  refinement_protocol.d_min_start=2.5 \
  basis_vector_combinations.max_refine=5 \
  basis_vector_combinations.max_try=10 \
  refinement.parameterisation.auto_reduction.action=fail *fix remove \
  refinement.reflections.weighting_strategy.override=statistical *stills constant external_deltapsi \
  refinement.outlier.algorithm=*null auto mcd tukey sauter_poon \
  table=True \
  ${files} > $(eval echo "${chip_name}.out") 2> dials.client.err < /dev/null

# stop the server
dials.find_spots_client stop

  #refinement.reflections.reflections_per_degree=None \
  #detector.fix=all beam.fix=all \
