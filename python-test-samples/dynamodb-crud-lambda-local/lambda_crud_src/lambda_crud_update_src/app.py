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

    body = json.loads(event['body'])
    item_id = body['Id']            
    name = body['name']             

    # Reference the DynamoDB table
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # Update item in DynamoDB
    try:
        response = table.update_item(
            Key={'Id': item_id},
            UpdateExpression="SET #name = :name",
            ExpressionAttributeNames={
                '#name': 'name'  # Using an alias for reserved words
            },
            ExpressionAttributeValues={
                ':name': name
            },
            ReturnValues="UPDATED_NEW"
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Item updated successfully',
                'response': response
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to update item', 'message': str(e)})
        }
