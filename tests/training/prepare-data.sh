#!/bin/bash

echo "localhost slots=1" > ./hostfile
export NUM_GPUS=1
export EXPERIMENT_NAME=retinanet-v0
export DASHBOARD_URL=http://127.0.0.1
export DATASET_NAME=coco

STAGE_DIR=/home/ubuntu/tmp

mkdir -p $STAGE_DIR/data 
mkdir -p $STAGE_DIR/output

wget -O $STAGE_DIR/data/train2017.zip http://images.cocodataset.org/zips/train2017.zip
unzip $STAGE_DIR/data/train2017.zip  -d $STAGE_DIR/data/images
rm $STAGE_DIR/data/train2017.zip

wget -O $STAGE_DIR/data/val2017.zip http://images.cocodataset.org/zips/val2017.zip
unzip $STAGE_DIR/data/val2017.zip -d $STAGE_DIR/data/images
rm $STAGE_DIR/data/val2017.zip

wget -O $STAGE_DIR/data/annotations_trainval2017.zip http://images.cocodataset.org/annotations/annotations_trainval2017.zip
unzip $STAGE_DIR/data/annotations_trainval2017.zip -d $STAGE_DIR/data
rm $STAGE_DIR/data/annotations_trainval2017.zip

git clone https://github.com/darkreapyre/keras-retinanet code

#docker build -t horovod:local --build-arg DASHBOARD_URL=https://127.0.0.1 --build-arg NUM_GPUS=1 --build-arg DATASET_NAME=coco --build-arg EXPERIMENT_NAME=retinanet-v0 -f Dockerfile .
#nvidia-docker run -it --rm -v /home/ubuntu/tmp/data:/data -v /home/ubuntu/tmp/output:/output -t horovod:local

#docker build -t container:local --build-arg DASHBOARD_URL=https://127.0.0.1 --build-arg NUM_GPUS=1 --build-arg DATASET_NAME=coco --build-arg EXPERIMENT_NAME=retinanet-v0 --build-arg MASTER_IMAGE=horovod:local -f Dockerfile .
#nvidia-docker run -it --rm -v /home/ubuntu/tmp/data:/data -v /home/ubuntu/tmp/output:/output -t container:local