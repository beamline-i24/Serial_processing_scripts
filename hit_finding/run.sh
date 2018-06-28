module load dials/nightly

# start the server in the background
nohup dials.find_spots_server nproc=16 > dials.server.out 2> dials.server.err < /dev/null &

# give server time to start
sleep 5

files=/dls/i24/data/2018/nt14493-94/acnir/hanson/*.cbf

time dials.find_spots_client \
  nproc=16 \
  json=find_spots.json \
  ${files} > dials.client.out 2> dials.client.err < /dev/null

# stop the server
dials.find_spots_client stop

