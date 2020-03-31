#!/bin/bash

for i in $(seq 1 $DEEPLEARNING_WORKERS_COUNT)
do
echo "Health check on worker: deeplearning-worker$i"
ssh -oStrictHostKeyChecking=no deeplearning-worker$i "touch /efs/deeplearning-worker$i-health.check"
done
