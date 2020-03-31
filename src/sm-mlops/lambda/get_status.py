import boto3
import os

# Global variables
sagemaker = boto3.client('sagemaker')
codebuild = boto3.client('codebuild')
cfn = boto3.client('cloudformation')

def describe_cfn(name):
    """ Get the details of the CloudFormation stack.
    Args:
        name (String): Name of the CloudFormation stack
    Returns:
        First item in the list
    """
    try:
        response = cfn.describe_stacks(StackName=name)['Stacks'][0]
    except Exception as e:
        print(e)
        print("Unable to get the cloudformation details")
        raise(e)
        
    return response

def get_cfn_output(name):
    """ Get the VPC Subnet and Security Groups and Container Image from the CloudFormation output.
    Args:
        name (String): Name of the CloudFormation Stack
    Returns:
        subnets (List): List of the Subnets in the VPC
        security_groups (List): List of security groups in the VPC
        container_images (List): List of Container images
    """
    subnets = []
    security_groups = []
    for output in describe_cfn(name)['Outputs']:
        if output['OutputKey'] == 'SecurityGroupId':
            security_groups.append(output['OutputValue'])
        if output['OutputKey'] == 'SubnetId':
            subnets.append(output['OutputValue'])
        if output['OutputKey'] == 'ContainerImage':
            container_image = output['OutputValue']
        if output['OutputKey'] == 'ContainerBuildProject':
            build_job_name = output['OutputValue']
        if output['OutputKey'] == 'PreprocessBuildProject':
            preprocess_job_name = output['OutputValue']
            
    return subnets, security_groups, container_image, preprocess_job_name, build_job_name

def get_build_id(name):
    """ Get a list of the build ID's for the Build project and return the latest.
    Args:
        name (string): Name of the Build Project
    Returns:
        First item in the list
    """
    try:
        ids = codebuild.list_builds_for_project(
            projectName=name
        )
        return ids.get('ids')[0]
    except Exception as e:
        print(e)
        print('Unable to get pre-processing build IDs.')
        raise(e)

def describe_build_job(name):
    """ Describe the CodeBuild job identified by input name.
    Args:
        name (string): Name of the CodeBuild Project
    Returns:
        (dict)
        Dictionary containing metadat and details about the status of the CodeBuild build.
    """
    try: 
        id = get_build_id(name)
        response = codebuild.batch_get_builds(
            ids=[str(id)]
        )
    except Exception as e:
        print(e)
        print('Unable to describe pre-processing build job.')
        raise(e)
        
    return response

def describe_training_job(name):
    """ Describe SageMaker training job identified by input name.
    Args:
        name (string): Name of SageMaker training job to describe.
    Returns:
        (dict)
        Dictionary containing metadata and details about the status of the training job.
    """
    try:
        response = sagemaker.describe_training_job(
            TrainingJobName=name
        )
    except Exception as e:
        print(e)
        print('Unable to describe training job.')
        raise(e)
        
    return response

def lambda_handler(event, context):
    stage = event['stage']
    if stage == 'Build':
        stack_name = event['stack_name']
        status = describe_cfn(stack_name)['StackStatus']
        print("{} current status = {}".format(stack_name, status)) # Debug
        # 'StackStatus': 'CREATE_IN_PROGRESS'|'CREATE_FAILED'|'CREATE_COMPLETE'
        if status == 'CREATE_IN_PROGESS':
            # Change status message to conform to SageMaker message output
            status = 'InProgress'
        elif status == 'CREATE_FAILED':
            event['message'] = "Build Job Failed"
            # Change status message to conform to SageMaker message output
            status = 'Failed'
        elif status =='CREATE_COMPLETE':
            build_job_name = get_cfn_output(stack_name)[4]
            codebuild_details = describe_build_job(build_job_name)
            status = codebuild_details['builds'][0]['buildStatus']
            print("{} current status = {}".format(build_job_name, status)) # Debug
            if status == 'FAILED':
                event['message'] = "Build Job Failed"
                # Change status message to conform to SageMaker message output
                status = 'Failed'
            elif status == 'SUCCEEDED':
                event['message'] = "Build Job Complete"
                event['subnets'] = get_cfn_output(stack_name)[0]
                event['security_groups'] = get_cfn_output(stack_name)[1]
                event['container'] = get_cfn_output(stack_name)[2]
                event['preprocess_job_name'] = get_cfn_output(stack_name)[3]
                # Change status message to conform to SageMaker message output
                status = 'Completed'
            elif status == 'IN_PROGRESS':
                # Change status message to conform to SageMaker message output
                status = 'InProgress'
    if stage == 'PreProcess':
        job_name = event['preprocess_job_name']
        preprocess_details = describe_build_job(job_name)
        status = preprocess_details['builds'][0]['buildStatus']
        print("{} current status = {}".format(job_name, status)) #Debug
        if status == 'FAILED':
            event['message'] = "Data Pre-Processing Job Failed"
            # Change status message to conform to SageMaker message output
            status = 'Failed'
        elif status == 'SUCCEEDED':
            event['message'] = "Data Pre-Processing Job Succeeded"
            # Change status message to conform to SageMaker message output
            status = 'Completed'
        elif status == "IN_PROGRESS":
            # Change status message to conform to SageMaker message output
            status = 'InProgress'
    if stage == 'Training':
        job_name = event['job_name']
        training_details = describe_training_job(job_name)
        status = training_details['TrainingJobStatus']
        print("{} current status = {}".format(job_name, status)) #Debug
        if status == 'Completed':
            """
            To-do: See how to integrate the output path into MlFlow Arctifacts.
                  A potential solution is add this to the notify function to
                  actually upload the artifacts and make the MlFlow API call.
            """
            s3_output_path = training_details['OutputDataConfig']['S3OutputPath']
            model_data_url = os.path.join(s3_output_path, job_name, 'output/model.tar.gz')
            event['message'] = 'Training job "{}" complete. Model data uploaded to "{}"'.format(job_name, model_data_url)
            event['model_data_url'] = model_data_url
        elif status == 'Failed':
            failure_reason = training_details['FailureReason']
            event['message'] = 'Training job failed. {}'.format(failure_reason)
        elif status == 'Stopping':
            # Continue until process is fully 'Stopped'
            status = 'InProgress'
        elif status == 'Stopped':
            # Set training status equivalent to 'Completed' as pre-trained inference mnodel will be used
            """
            Todo: See how to integrate the output path into MlFlow Arctifacts
            """
            s3_output_path = training_details['OutputDataConfig']['S3OutputPath']
            # model_data_url = os.path.join(s3_output_path, 'pre-trained_model/model.tar.gz')
            event['message'] = 'Training job "{}" has been manually stopped.'.format(job_name)
            # event['model_data_url'] = model_data_url
            status = 'Completed'
            
    event['status'] = status
    
    return event