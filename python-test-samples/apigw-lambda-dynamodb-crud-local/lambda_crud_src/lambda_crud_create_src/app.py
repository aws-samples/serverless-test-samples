import os
import json
import boto3
def lambda_handler(event, context):
    # Checking if running locally
    if os.environ.get('AWS_SAM_LOCAL'):
        # Use local DynamoDB endpoint
        dynamodb = boto3.resource('dynamodb', endpoint_url='http://172.17.0.1:8000')
    else:
        # Use the default DynamoDB endpoint (AWS)
        dynamodb = boto3.resource('dynamodb')

    # Adding an item to DynamoDB
    item = json.loads(event['body'])

    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    response = table.put_item(Item=item)

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Item added', 'response': response})
    }
