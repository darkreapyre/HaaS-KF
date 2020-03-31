import boto3
from botocore.exceptions import ClientError
import os
import json

# Global variables
bootstrap_bucket = os.environ['BOOTSTRAP_BUCKET']
master_image = os.environ['MASTER_IMAGE']
cfn = boto3.client('cloudformation')
s3 = boto3.resource('s3')
gpu_instances = {
    'ml.p3.2xlarge': 1,
    'ml.p3.8xlarge': 4,
    'ml.p3.16xlarge': 8,
    'ml.p2.xlarge': 1,
    'ml.p2.8xlarge': 8,
    'ml.p2.16xlarge': 16
}

def cfn_params(config):
    params = []
    params.append({'ParameterKey': 'S3BootstrapBucket', 'ParameterValue': bootstrap_bucket})
    params.append({'ParameterKey': 'S3ExperimentBucket', 'ParameterValue': config['Experiment_Bucket']})
    params.append({'ParameterKey': 'NumGPUs', 'ParameterValue': str(gpu_instances.get(config['Training_Instance']))})
    params.append({'ParameterKey': 'DashboardURL', 'ParameterValue': config['Dashboard_URL']})
    params.append({'ParameterKey': 'DatasetName', 'ParameterValue': config['Dataset_Name']})
    params.append({'ParameterKey': 'ModelPrefix', 'ParameterValue': config['Experiment_Prefix'].lower()})
    params.append({'ParameterKey': 'GitHubUser', 'ParameterValue': config['GitHub_User']})
    params.append({'ParameterKey': 'GitHubRepo', 'ParameterValue': config['GitHub_Repo']})
    params.append({'ParameterKey': 'MasterImage', 'ParameterValue': master_image})
    
    return params

def stack_create(name, template, parameters):
    try:
        response = cfn.create_stack(
            StackName=name,
            TemplateBody=template,
            Parameters=parameters,
            Capabilities=[
                'CAPABILITY_IAM'
            ],
            OnFailure='DO_NOTHING'
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'AlreadyExistsException':
            print("Stack: {} already exists, only one stack per experiment ...".format(name))
            raise(e)
        else:
            print("Error creating stack: %s" % e)
            raise(e)

def lambda_handler(event, context):
    # Get master training configuration
    config = event['Configuration']
    
    # Get cfn template depending on the desired training platform
    cfn_key = 'artifacts/'+config['Platform']+'-build-template.json'
    s3.Bucket(bootstrap_bucket).download_file(cfn_key, '/tmp/template.json')
    cfn_template = open('/tmp/template.json', 'r').read()

    # Create CLOUDFORMATION parameters
    params = cfn_params(config)
    print(params) #debug
    
    # Start cfn stack creation
    stack_name = str(config['Experiment_Prefix']) + '-Stack'
    print("starting {} build job ...".format(stack_name))
    stack_create(stack_name, cfn_template, params)
    event['stack_name'] = stack_name
    event['stage'] = 'Build'
    event['status'] = 'InProgress' #change status message to conform to SageMaker message output
    event['message'] = 'Started Build job "{}"'.format(stack_name)
    
    return event