#!/bin/bash

# This script should only be run on master node to reset cluster

# This script should ONLY be run if no training is currently running
RUN_COUNT=`ps -elf | grep mpirun | wc -l`
if [ $RUN_COUNT -gt 1 ]
then
echo "mpirun is running so can not setup cluster"
exit 0
fi
 
# Name of S3 bucket
S3_BUCKET=

# path in S3 bucket where input is available
INPUT_PREFIX=mask-rcnn/deeplearning-ami/input

# Name of run script available at s3://$S3_BUCKET/$INPUT_PREFIX
RUN_SCRIPT=run.sh

# Name of setup script available at s3://$S3_BUCKET/$INPUT_PREFIX
SETUP_SCRIPT=setup.sh

# Name of data tar available at s3://$S3_BUCKET/$INPUT_PREFIX
DATA_TAR=coco-2017.tar

# Name of code tar available at s3://$S3_BUCKET/$INPUT_PREFIX
CODE_TAR=tensorpack.tar

rm $HOME/$RUN_SCRIPT
aws s3 cp s3://$S3_BUCKET/$INPUT_PREFIX/$RUN_SCRIPT $HOME/$RUN_SCRIPT
chmod u+x $HOME/$RUN_SCRIPT

rm  $HOME/$SETUP_SCRIPT
aws s3 cp s3://$S3_BUCKET/$INPUT_PREFIX/$SETUP_SCRIPT $HOME/$SETUP_SCRIPT
chmod u+x $HOME/$SETUP_SCRIPT

rm $HOME/$DATA_TAR
aws s3 cp s3://$S3_BUCKET/$INPUT_PREFIX/$DATA_TAR $HOME/$DATA_TAR

rm $HOME/$CODE_TAR
aws s3 cp s3://$S3_BUCKET/$INPUT_PREFIX/$CODE_TAR $HOME/$CODE_TAR

echo "Cluster setup started"
for i in $(seq 1 $DEEPLEARNING_WORKERS_COUNT)
do
echo "setting up deeplearning-worker$i"
scp -oStrictHostKeyChecking=no $HOME/$SETUP_SCRIPT ubuntu@deeplearning-worker$i:~/ 

echo "copy $HOME/$DATA_TAR to  deeplearning-worker$i, may take a while"
scp $HOME/$DATA_TAR ubuntu@deeplearning-worker$i:~/ 

echo "extract $HOME/$DATA_TAR to  deeplearning-worker$i, may take a while"
ssh ubuntu@deeplearning-worker$i "tar -xvf ~/$DATA_TAR"

echo "copy $HOME/$CODE_TAR to  deeplearning-worker$i, may take a while"
scp $HOME/$CODE_TAR ubuntu@deeplearning-worker$i:~/ 

echo "extract $HOME/$CODE_TAR to  deeplearning-worker$i, may take a while"
ssh ubuntu@deeplearning-worker$i "tar -xvf ~/$CODE_TAR"
done

echo "Cluster setup complete"
