from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import event_source, S3Event
import boto3
import os
  
destination_bucket = os.environ['DESTINATION_BUCKET']
s3 = boto3.resource('s3')
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

            # get object from source bucket
            object_key = record.s3.get_object.key
            originalObject = s3.Object(bucket_name, object_key)
            logger.info(originalObject)

            # transform message to uppercase
            lowerCaseMessage = originalObject.get()['Body'].read().decode('utf-8')
            upperCaseMessage = lowerCaseMessage.upper()
            logger.info(upperCaseMessage)

            # put uppercase message into destination bucket
            object = s3.Object(
                bucket_name=destination_bucket, 
                key=object_key
            )

            object.put(Body=upperCaseMessage)

    except Exception as e:
        logger.exception(e)
        raise
