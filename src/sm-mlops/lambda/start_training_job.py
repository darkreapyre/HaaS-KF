from datetime import datetime
import boto3
import os
import ast

# Global variables
SAGEMAKER_ROLE = os.environ['SAGEMAKER_ROLE'] # Role to pass to SageMaker training job that has access to training data in S3, etc

def create_training_job(job_name, train_manifest_uri, container, s3_output_path, hyperparameters, instance_type, count, security_groups, subnets):
    """ Start SageMaker training job
    Args:
        job_name (string): Name to label training job with
        train_manifest_uri (string): URI to training data manifest file in S3
        container (string): Registry path of the Docker image that contains the training algorithm
        s3_output_path (string): Path of where in S3 bucket to output model artifacts after training
        hyperparameters (dict): Python dictionary of hyperparameters
        instance_type (string): Training instance type
        count (int): # of training instances
    Returns:
        (None)
    """
    sagemaker = boto3.client('sagemaker')
    try:
        response = sagemaker.create_training_job(
            TrainingJobName=job_name,
            HyperParameters=hyperparameters,
            AlgorithmSpecification={
                'TrainingImage': container,
                'TrainingInputMode': 'File'
            },
            RoleArn=SAGEMAKER_ROLE,
            InputDataConfig=[
                {
                    'ChannelName': 'train',
                    'DataSource': {
                        'S3DataSource': {
                            'S3DataType': 'S3Prefix',
                            'S3Uri': train_manifest_uri,
                            'S3DataDistributionType': 'FullyReplicated'
                        }
                    },
                    'RecordWrapperType': 'None',
                    'CompressionType': 'None'
                }
            ],
            OutputDataConfig={
                'S3OutputPath': s3_output_path
            },
            ResourceConfig={
                'InstanceType': instance_type,
                'InstanceCount': count,
                'VolumeSizeInGB': 200
            },
            VpcConfig={
                'SecurityGroupIds': security_groups,
                'Subnets': subnets
            },
            StoppingCondition={
                'MaxRuntimeInSeconds': 86400
            }
        )
    except Exception as e:
        print(e)
        print('Unable to create training job.')
        raise(e)

def lambda_handler(event, context):
    # Get master configuration
    config = event.get('Configuration')

    # Create training job parameters
    hyperparameters = ast.literal_eval(config.get('Hyperparameters')) # Note: All values must be STRING type   
    instance_type = str(config['Training_Instance'])
    count = int(config['Instance_Count'])
    train_manifest_uri = str('s3://'+config['Experiment_Bucket']+'/'+config['Experiment_Prefix']+'/training_data')
    s3_output_path = str('s3://'+config['Experiment_Bucket']+'/'+config['Experiment_Prefix'])
    model_prefix = str(config['Experiment_Prefix'])
    container = str(event.get('container'))
    security_groups = (event.get('security_groups'))
    subnets = (event.get('subnets'))

    # Configure job name
    time_stamp = str(datetime.now()).split(' ')
    date = time_stamp[0]
    time = time_stamp[1].replace(':', '-').split('.')[0]
    ID = time_stamp[1].split('.')[1][-3:]
    job_name = '{}-{}-{}-{}'.format(model_prefix, date, time, ID)
    print('Starting {} training job ...'.format(job_name))
    create_training_job(job_name, train_manifest_uri, container, s3_output_path, hyperparameters, instance_type, count, security_groups, subnets)
    event['job_name'] = job_name
    event['stage'] = 'Training'
    event['status'] = 'InProgress'
    event['message'] = 'Started SageMaker Training job "{}"'.format(job_name)
    
    return event