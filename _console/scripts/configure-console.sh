# Install jq
echo -en "\nUpdating AWS CLI ...\n"
sudo yum -y install jq

# Update awscli
sudo -H pip install -U awscli

# Install bash-completion
sudo yum install bash-completion -y

# Configure AWS CLI
echo -en "\nConfigure AWS CLI ...\n"
export AWS_DEFAULT_REGION=$(curl -s 169.254.169.254/latest/dynamic/instance-identity/document | jq -r .region)
aws configure set default.region ${AWS_DEFAULT_REGION}


# Deployment-specific variables 
export AWS_ACCOUNT_ID=`aws sts get-caller-identity --query 'Account'`
export AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID#\"}
export AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID%\"}
export AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID
export AWS_AVAILABILITY_ZONES="$(aws ec2 describe-availability-zones --query 'AvailabilityZones[].ZoneName' --output text | awk -v OFS="," '$1=$1')"
export AWS_INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
aws ec2 describe-instances --instance-ids $AWS_INSTANCE_ID > /tmp/instance.json
export AWS_STACK_NAME=$(jq -r '.Reservations[0].Instances[0]|(.Tags[]|select(.Key=="aws:cloudformation:stack-name")|.Value)' /tmp/instance.json)
export AWS_ENVIRONMENT=$(jq -r '.Reservations[0].Instances[0]|(.Tags[]|select(.Key=="aws:cloud9:environment")|.Value)' /tmp/instance.json)
export C9_MASTER_STACK=${AWS_STACK_NAME%$AWS_ENVIRONMENT}
export C9_MASTER_STACK=${C9_MASTER_STACK%?}
export C9_MASTER_STACK=${C9_MASTER_STACK#aws-cloud9-}
export AWS_MASTER_STACK=${C9_MASTER_STACK%-Console}
export S3_BUCKET=s3://$(aws cloudformation describe-stack-resource --stack-name $AWS_MASTER_STACK --logical-resource-id "Bucket" | jq -r '.StackResourceDetail.PhysicalResourceId')
#export S3_PREFIX=${AWS_MASTER_STACK}/input

# Generate SSH Key
#echo -en "\nCreating SSH Key ...\n"
#CURRENT_KEY=$(aws ec2 describe-key-pairs --key-name $AWS_MASTER_STACK --query 'KeyPairs[].KeyName' --output text 2>/dev/null)
#if [[ $CURRENT_KEY==$AWS_MASTER_STACK ]]; then
#    echo -en "\nExisting Key Pair found, deleting ...\n"
#    rm -f $HOME/.ssh/id_rsa*
#    aws ec2 delete-key-pair --key-name $AWS_MASTER_STACK
#fi
#ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
#aws ec2 import-key-pair --key-name "${AWS_MASTER_STACK}" --public-key-material file://~/.ssh/id_rsa.pub

# Persist deployment-specific  variables
echo -en "\nSaving configuration ...\n"
echo "export AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID" >> ~/.bashrc
echo "export AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION" >> ~/.bashrc
echo "export AWS_AVAILABILITY_ZONES=$AWS_AVAILABILITY_ZONES" >> ~/.bashrc
echo "export AWS_STACK_NAME=$AWS_STACK_NAME" >> ~/.bashrc
echo "export C9_MASTER_STACK"=$C9_MASTER_STACK >> ~/.bashrc
echo "export AWS_MASTER_STACK=$AWS_MASTER_STACK" >> ~/.bashrc
echo "export S3_BUCKET=$S3_BUCKET" >> ~/.bashrc
#echo "export S3_PREFIX=$S3_PREFIX" >> ~/.bashrc
echo -en "\nConsole configuration complete!\n"

# Upload the master contents for the model to S3 to simulate the GitOps `push`
curl -L -o /tmp/master.zip http://github.com/darkreapyre/HaaS/master/
aws s3 cp /tmp/master.zip $S3_BUCKET/master.zip