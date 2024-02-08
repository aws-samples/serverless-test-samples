import json
import boto3
import time
import os
import io

def lambda_handler(event, context):
    data = json.loads(event["Records"][0]["body"])
    #order_id = event['orderId']
    order_id = data['orderId']

    dynamodb = boto3.resource('dynamodb')
    s3_client = boto3.client('s3')
    table = dynamodb.Table('order_details')
    recordFound = False
    data = ""
    try:
        for i in range(5):
            response = table.get_item(Key={'orderId': order_id})
            if "Item" not in response:
                print(f"Order ID {order_id} not exists in table. Retrying for {i}")
                time.sleep(5)  
            else :
                print(f"Order ID {order_id} exists in table after retry of {i}")
                recordFound = True
                break
        if recordFound:
            data = f"Order ID {order_id} exists in table "
        else :
            data = f"Order ID {order_id} not found in table "
        
        temp_file = io.BytesIO()
        temp_file.write(data.encode())
        timestamp = time.time_ns()
        filename = os.path.join("results", f"{timestamp}.txt")
        s3_client.put_object(Body=temp_file.getvalue(), Bucket='serverless-test-uc2', Key=filename)
        temp_file.close()
        print(f"File uploaded to S3: s3://serverless-test-/{filename}")	
    except Exception as e:
        print(f"Error fetching order ID {order_id} into table: {e}")
        raise e