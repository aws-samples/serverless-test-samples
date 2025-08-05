import json

def lambda_handler(event, context):
    response = {
        'statusCode': 200,
        'body': json.dumps('This is mock response')
    }
    return response