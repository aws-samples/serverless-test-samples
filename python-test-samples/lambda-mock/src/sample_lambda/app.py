"""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""

# Start of lambda handler code:  src/sampleLambda/app.py
from os import environ
from typing import Any, Dict
from boto3 import resource
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import validator

# Import the schema for the Lambda Powertools Validator
from schemas import INPUT_SCHEMA, OUTPUT_SCHEMA

# [1] Globally scoped resources
# Initialize the resources once per Lambda execution environment by using global scope.
_LAMBDA_DYNAMODB_RESOURCE = { "resource" : resource('dynamodb'), 
                              "table_name" : environ.get("DYNAMODB_TABLE_NAME","NONE") }
_LAMBDA_S3_RESOURCE = { "resource" : resource('s3'), 
                        "bucket_name" : environ.get("S3_BUCKET_NAME","NONE") }

# [2] Define a Global class an AWS Resource: Amazon DynamoDB. 
class LambdaDynamoDBClass:
    """
    AWS DynamoDB Resource Class
    """
    def __init__(self, lambda_dynamodb_resource):
        """
        Initialize a DynamoDB Resource
        """
        self.resource = lambda_dynamodb_resource["resource"]
        self.table_name = lambda_dynamodb_resource["table_name"]
        self.table = self.resource.Table(self.table_name)

# [3] Define a Global class an AWS Resource: Amazon S3 bucket.
class LambdaS3Class:
    """
    AWS S3 Resource Class
    """
    def __init__(self, lambda_s3_resource):  
        """
        Initialize an S3 Resource
        """
        self.resource = lambda_s3_resource["resource"]
        self.bucket_name = lambda_s3_resource["bucket_name"]
        self.bucket = self.resource.Bucket(self.bucket_name)

# [4] Validate the event schema and return schema using Lambda Power Tools
@validator(inbound_schema=INPUT_SCHEMA, outbound_schema=OUTPUT_SCHEMA)
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext) -> Dict[str, Any]:
    """
    Lambda Entry Point
    """
    # [5] Use the Global variables to optimize AWS resource connections
    global _LAMBDA_DYNAMODB_RESOURCE
    global _LAMBDA_S3_RESOURCE

    dynamodb_resource_class = LambdaDynamoDBClass(_LAMBDA_DYNAMODB_RESOURCE)
    s3_resource_class = LambdaS3Class(_LAMBDA_S3_RESOURCE)

    # [6] Explicitly pass the global resource to subsequent functions
    return create_letter_in_s3(
            dynamo_db = dynamodb_resource_class,
            s3 = s3_resource_class,
            doc_type = event["pathParameters"]["docType"],
            cust_id = event["pathParameters"]["customerId"])

def create_letter_in_s3( dynamo_db: LambdaDynamoDBClass,
                         s3: LambdaS3Class,
                         doc_type: str,
                         cust_id: str) -> dict:

    """
    Given a document type and a customer id, create a text document in S3
    Document contents and customer name are retrieved from DynamoDB
    """

    status_code = 200
    body = "OK"
    
    try:         
        # [7] Use the passed environment class for AWS resource access - DynamoDB
        customer_name = dynamo_db.table.get_item(Key={"PK": f"C#{cust_id}"})["Item"]["data"]
        document_text = dynamo_db.table.get_item(Key={"PK": f"D#{doc_type}"})["Item"]["data"]

        # [8] Use the passed environment class for AWS resource access - S3
        s3_file_key = f"{cust_id}/{doc_type}.txt"
        s3.bucket.put_object(Key=s3_file_key, 
                        Body=f"Dear {customer_name};\n{document_text}".encode('utf-8'),
                        ServerSideEncryption='AES256')

        body = f"{body} {s3_file_key}"
    except KeyError as index_error:
        body = "Not Found: " + str(index_error)
        status_code = 404
    except Exception as other_error:               
        body = "ERROR: " + str(other_error)
        status_code = 500
    finally:
        return {"statusCode": status_code, "body" : body }

# End of lambda handler code
