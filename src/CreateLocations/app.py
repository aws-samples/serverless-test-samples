import json,boto3,os

def lambda_handler(event, context):
    # TODO implement
    dynamodb = boto3.resource('dynamodb')
    dynamodb_table_name = os.environ["DYNAMODB_TABLE_NAME"]
    table = dynamodb.Table(dynamodb_table_name)
    location_set = set()
    response = table.scan()
    data = response['Items']
    for item in response['Items']:
        print(item["LOCATION"])
        unicorn_location=item["LOCATION"]
        location_set.add(unicorn_location)
    location_list = [x for x in sorted(location_set)]
    response = table.put_item(
        Item={
            'PK': "LOCATION#LIST",
            'LOCATIONS': location_list
        }
    )
    status_code = response['ResponseMetadata']['HTTPStatusCode']


    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
