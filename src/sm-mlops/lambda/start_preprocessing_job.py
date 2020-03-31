from datetime import datetime
import boto3
import os
import json

def build_var(config):
    variables = []
    for k, v in config.items():
        variables.append({'name': k, 'value': v, 'type': 'PLAINTEXT'})
        
    return variables

def start_build(job_name, variables):
    codebuild = boto3.client('codebuild')
    try:
        response = codebuild.start_build(
            projectName=job_name,
            environmentVariablesOverride=variables,
        )
    
    except Exception as e:
        print(e)
        print('unable to start codebuild job for data pre-processing ...')
        raise(e)

def lambda_handler(event, context):
    # Get master training configuration
    config = event.get('Configuration')

    # Create CODEBUILD environmental variables
    variables = build_var(config)

    # Start the Build Job
    job_name = event['preprocess_job_name']
    print('starting {} data pre-processing job ...'.format(job_name))
    start_build(job_name, variables)
    event['stage'] = 'PreProcess'
    event['status'] = 'InProgress' #change status message to conform to SageMaker message output
    event['message'] = 'Started Pre-Processing Data job "{}"'.format(job_name)
    
    return event