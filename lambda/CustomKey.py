"""
CloudFormation Custom Resource to create EC2 KeyPair and upload the `.pem` to S3.

NOTE: The KeyPair will be used by the ` ` Lambda function to log into the cluster master and start `run.sh`
"""
import os
import logging
import json
import botocore
import boto3
from botocore.vendored import requests

DEFAULT_LOGGING_LEVEL = logging.INFO
logging.basicConfig(format='[%(levelname)s] %(message)s', level=DEFAULT_LOGGING_LEVEL)
logger = logging.getLogger(__name__)
logger.setLevel(DEFAULT_LOGGING_LEVEL)
boto3.set_stream_logger('boto3', level=DEFAULT_LOGGING_LEVEL)

SUCCESS = "SUCCESS"
FAILED = "FAILED"