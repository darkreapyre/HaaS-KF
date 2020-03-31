import logging
import boto3
import uuid
import botocore
import json
import traceback
import cfnresponse
import cfnresponse

# Global variables
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# S3 Event configuration
def configure_s3(properties):
    lambda_client = boto3.client('lambda')
    s3_client = boto3.client('s3')
    configuration = {}
    configuration['LambdaFunctionConfigurations'] = [
        {
            'LambdaFunctionArn': properties.get('launch_function_arn'),
            'Events': [
                's3:ObjectCreated:Put'
            ],
            'Filter': {
                'Key': {
                    'FilterRules': [
                        {
                            'Name': 'suffix',
                            'Value': 'experiment_config.json'
                        }
                    ]
                }
            }
        }
    ]
    # Create Permission to trigger the LaunchLambda
    lambda_response = lambda_client.add_permission(
        FunctionName=properties.get('launch_function_arn'),
        StatementId = str(uuid.uuid4()),
        Action='lambda:InvokeFunction',
        Principal='s3.amazonaws.com',
        SourceArn='arn:aws:s3:::'+properties.get('s3_bucket'),
        SourceAccount=properties.get('account_id')
    )
    response = s3_client.put_bucket_notification_configuration(
        Bucket=properties.get('s3_bucket'),
        NotificationConfiguration=configuration
    )

def lambda_handler(event, context):
    logger.debug('Event: {}'.format(event)) #debug
    logger.debug('Context: {}'.format(context)) #debug
    properties = event['ResourceProperties']
    responseData = {}
    if event['RequestType'] == 'Create':
        # Configure S3 Event
        try:
            configure_s3(properties)
            logger.info('successfully configured S3 event')
            responseData = {'Success': 'S3 launch event configured ...'}
            cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData, 'CustomResourcePhysicalID')
        except Exception as e:
            logger.error(e, exc_info=True)
            responseData = {'Error': traceback.format_exc(e)}
            cfnresponse.send(event, context, cfnresponse.FAILED, responseData, 'CustomResourcePhysicalID')
    if event['RequestType'] == 'Delete':
        # Immediately respond on Delete
        cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData, 'CustomResourcePhysicalID')