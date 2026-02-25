import os
import boto3
import json

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

    # Parse the JSON body
    body = json.loads(event['body'])

    # Access the Id element
    item_id = body['Id']

    try:
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

    except Exception as e:
        # Failed reading from DynamoDB
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to read item', 'message': str(e)})
        }
