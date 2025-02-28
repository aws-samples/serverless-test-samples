import os
import boto3

def lambda_handler(event, context):
    # Check if running locally
    if os.environ.get('AWS_SAM_LOCAL'):
        # Use local DynamoDB endpoint
        dynamodb = boto3.resource('dynamodb', endpoint_url='http://172.17.0.1:8000')
    else:
        # Use the default DynamoDB endpoint (AWS)
        dynamodb = boto3.resource('dynamodb')

    # Access your DynamoDB table
    table_name = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # Define the table creation parameters
    table_creation_params = {
        'TableName': 'CRUDLocalTable',
        'KeySchema': [
            {
                'AttributeName': 'Id',
                'KeyType': 'HASH'  # Partition key
            }
        ],
        'AttributeDefinitions': [
            {
                'AttributeName': 'Id',
                'AttributeType': 'S'  # String type
            }
        ],
        'ProvisionedThroughput': {
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    }

    # Create the DynamoDB table
    table = dynamodb.create_table(**table_creation_params)

    # Wait until the table exists before continuing
    table.wait_until_exists()

    print("Table created successfully:", table.table_name)

    return {
        'statusCode': 200,
        'body': table.table_name
    }
