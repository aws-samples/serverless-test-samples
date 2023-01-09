from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import event_source, S3Event
import boto3
import os
  
destination_bucket = os.environ['DESTINATION_BUCKET']
results_table = os.environ['RESULTS_TABLE']

s3 = boto3.resource('s3')
dynamodb = boto3.client('dynamodb')
logger = Logger(service="APP")
tracer = Tracer(service="APP")

@tracer.capture_lambda_handler
@logger.inject_lambda_context(
    log_event=True
)
@event_source(data_class=S3Event)
def handler(event: S3Event, context):
    try:
        bucket_name = event.bucket_name
        for record in event.records:

            # get object from destination bucket
            object_key = record.s3.get_object.key
            transformedObject = s3.Object(bucket_name, object_key)
            transformedMessage = transformedObject.get()['Body'].read().decode('utf-8')
            logger.info(transformedMessage)

            # put object into dynamodb 
            response = dynamodb.put_item(TableName=results_table, Item={'id':{'S':object_key},'message':{'S':transformedMessage}})
            logger.info(response)

    except Exception as e:
        logger.exception(e)
        raise
