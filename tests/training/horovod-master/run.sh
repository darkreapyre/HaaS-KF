#!/bin/bash

HOROVOD_CYCLE_TIME=0.5 \
HOROVOD_FUSION_THRESHOLD=67108864 \
mpirun -np 1 \
--hostfile ./hostfile \
--mca plm_rsh_no_tree_spawn 1 -bind-to none -map-by slot -mca pml ob1 -mca btl ^openib \
-mca btl_tcp_if_exclude lo,docker0 \
-mca oob_tcp_if_exclude lo,docker0 \
-mca btl_vader_single_copy_mechanism none \
-x NCCL_SOCKET_IFNAME=^docker0,lo \
-x NCCL_MIN_NRINGS=8 -x NCCL_DEBUG=INFO \
-x LD_LIBRARY_PATH -x PATH \
-x HOROVOD_CYCLE_TIME -x HOROVOD_FUSION_THRESHOLD \
--output-filename /output \
python3 /train.py --backbone resnet50 --steps 128 --epochs 2 --batch-size 1 --dataset coco --dataset-path /data --output-path /output --tracking-uri http://127.0.0.1 --experiment-name retinanet-v0