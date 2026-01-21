import os
import json
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
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    item_id = event['Id']
    response = table.get_item(Key={'Id': item_id})

    item = response.get('Item', {})

    if item:
        # Item found, return it
        return {
            'statusCode': 200,
            'body': json.dumps(item)
        }
    else:
        # Item not found, return a 404 status
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Item not found', 'message': f'No item with Id {item_id} found'})
        }
