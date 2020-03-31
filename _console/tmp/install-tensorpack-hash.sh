#!/bin/bash

for i in $(seq 1 $DEEPLEARNING_WORKERS_COUNT)
do
ssh -oStrictHostKeyChecking=no ubuntu@deeplearning-worker$i "uptime"
ssh ubuntu@deeplearning-worker$i "rm -rf ./tensorpack; git clone https://github.com/tensorpack/tensorpack.git; cd ./tensorpack; git fetch origin 860f7a382f8dc245e46c5f637866ef6384db1733; git reset --hard 860f7a382f8dc245e46c5f637866ef6384db1733"
done
