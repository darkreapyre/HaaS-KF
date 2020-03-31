import os
import boto3

# global variables
SNS_TOPIC = os.environ['SNS_TOPIC']

def post_message(message):
    """ Posts message to SNS.
    Args:
        message (string): Message to post to SNS
    Returns:
        (None)
    """
    sns = boto3.client('sns')
    try:
        sns.publish(TargetArn=SNS_TOPIC, Message=message)
    except Exception as e:
        print(e)
        print('Unable to publish SNS message.')
        raise(e)

def lambda_handler(event, context):
    message = event['message']
    print('Message: {}'.format(message))
    post_message(message)
    
    return event