import os
import boto3
import botocore
import traceback
import json

# Global variables
sfn = boto3.client('stepfunctions')
s3 = boto3.resource('s3')

def build_config(data, bucket, versionId):
    config = data
    experiment_prefix = str(data['Model_Name'].lower()+'-v'+data['Version'])
    config['Experiment_Bucket']= bucket
    config['Experiment_Prefix'] = experiment_prefix
    obj = s3.Object(bucket, experiment_prefix+'/'+experiment_prefix+'.json')
    obj.put(Body=json.dumps(config))
    return str(experiment_prefix)+'-'+versionId, config

def lambda_handler(event, context):
    print(json.dumps(event)) # Debug
    # Extract S3 data
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    versionId = event['Records'][0]['s3']['object']['versionId'][-7:]
    # Get master training job configurtion
    obj = s3.Object(bucket, key)
    data = json.loads(obj.get()['Body'].read())
    if data['Platform'] == 'sagemaker':
        sfn_arn = os.environ['SageMaker_ARN']
    elif data['Platform'] == 'eks':
        sfn_arn = os.environ['EKS_ARN']
    elif data['Platform'] == 'dlami':
        sfn_arn = os.environ['AMI_ARN']
    sfn_input = {}
    sfn_job_name, sfn_input['Configuration'] = build_config(data, bucket, versionId)
    # Execute StateMachine
    try:
        sfn_response = sfn.start_execution(
            stateMachineArn=str(sfn_arn),
            name=sfn_job_name,
            input=json.dumps(sfn_input)
        )
        print('started state machine execution ...')
    except Exception as e:
        print(e)
        print('failed to start state machine execution ...')
        traceback.print_exc()
    return "Complete"