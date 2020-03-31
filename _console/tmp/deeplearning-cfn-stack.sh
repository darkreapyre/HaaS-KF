#!/bin/bash


# Cutomize bucket name
S3_BUCKET=

#Customize stack name as needed
STACK_NAME=mask-rcnn

# cfn template name
CFN_TEMPLATE=deeplearning-cfn-template.json

# Cutomize bucket prefix if needed
S3_PREFIX=mask-rcnn/deeplearning-ami/input

# Customize CIDR for SSH 
SSH_LOCATION=0.0.0.0/0

# Data Tar file
DATA_TAR=coco-2017.tar

# Source tar file
SOURCE_TAR=tensorpack.tar

# Number of workers, minimum 1, maximum n - 1 for cluster of size n
# Master node is also used as a worker node, hence n - 1 for cluster of size n
NUM_WORKERS=1

# EC2 AMI override; leave blank if using default AMI defined in template
AMI_ID=

# Leave blank if you need to create a new EFS file system
EFS_ID=

# EC2 instance type
INSTANCE_TYPE=p3.16xlarge

# EC2 key pair name
KEY_NAME=

# AWS Region; customize as needed 
AWS_REGION=us-east-1

# AWS Availability zone; customize as needed 
AWS_AZ=us-east-1d

# Use EFS to serve data
EFS_SERVES=false

aws cloudformation create-stack --region $AWS_REGION  --stack-name $STACK_NAME \
--template-body file://$CFN_TEMPLATE \
--capabilities CAPABILITY_NAMED_IAM \
--parameters \
ParameterKey=ActivateCondaEnv,ParameterValue=tensorflow_p36 \
ParameterKey=AMIOverride,ParameterValue=$AMI_ID \
ParameterKey=EFSFileSystemId,ParameterValue=$EFS_ID \
ParameterKey=EFSMountPoint,ParameterValue=efs \
ParameterKey=EFSServesData,ParameterValue=$EFS_SERVES \
ParameterKey=EbsVolumeSize,ParameterValue=200 \
ParameterKey=ImageType,ParameterValue=Ubuntu \
ParameterKey=InstanceType,ParameterValue=$INSTANCE_TYPE \
ParameterKey=KeyName,ParameterValue=$KEY_NAME \
ParameterKey=MyAvailabilityZone,ParameterValue=$AWS_AZ \
ParameterKey=S3Bucket,ParameterValue=$S3_BUCKET \
ParameterKey=RunScript,ParameterValue=$S3_PREFIX/run.sh \
ParameterKey=SetupScript,ParameterValue=$S3_PREFIX/setup.sh \
ParameterKey=SSHLocation,ParameterValue=$SSH_LOCATION \
ParameterKey=TarData,ParameterValue=$S3_PREFIX/$DATA_TAR \
ParameterKey=TarSource,ParameterValue=$S3_PREFIX/$SOURCE_TAR \
ParameterKey=WorkerCount,ParameterValue=$NUM_WORKERS
