#!/bin/bash

for i in $(seq 1 $DEEPLEARNING_WORKERS_COUNT)
do
echo "Mount fsx on worker: deeplearning-worker$i"
ssh ubuntu@deeplearning-worker$i 'sudo mkdir /fsx'
ssh ubuntu@deeplearning-worker$i 'sudo mount -t lustre <filesystemid>.fsx.<region>.amazonaws.com@tcp:/fsx /fsx'
done
