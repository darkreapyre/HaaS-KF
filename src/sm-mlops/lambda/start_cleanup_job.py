import boto3
from botocore.exceptions import ClientError
import os
import json

# Global variables
cfn = boto3.client('cloudformation')

def stack_delete(name):
    """ Delete training clodformation stack.
    Args:
        name (string): Name of the cloudformation stack.
    Returns:
        (None)
    """
    try:
        response = cfn.delete_stack(
            StackName=name
        )
    except ClientError as e:
        print("Unable to delete training stack ...")
        raise(e)

def lambda_handler(event, context):  
    # Start cfn stack deletion
    stack_name = event['stack_name']
    print("deleting training stack {} ...".format(stack_name))
    stack_delete(stack_name)
    event['stage'] = 'CleanUp'
    event['status'] = 'Completed' #immediately set the job to complete
    event['message'] = 'Cleanup initiated ...\n'.format(stack_name)
    event['message'] += 'Training complete!'
    
    return event