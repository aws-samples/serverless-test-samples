## Description 
Integration Testing - Serverless Asynchronous

![Serverless async Test Architecture.png](Serverless%20async%20Test%20Architecture.png)

### Deploying Lambda:
1.Lambda
  - Application code is deployed as Zip file or executable in the Lambda function code with updated runtime and Handler

2.Environment Variables 
  - Configure the lambda environment variables with API_URL,REGION,TARGET_QUEUE (Queue where the message is to be received)

## Test Scenario-1

### Pre-requisites
1. An Existing serverless asynchronous application.
2. SQS trigger set for Lambda function
3. Lambda Function
4. Destination SQS configured for Lambda function

### Logging to cloudwatch Steps:
1. SQS to send messages with required Payload.
2. This triggers the lambda which invokes the API configured.
3. Lambda will trigger the API and awaits response.
4. Once the API sends the response the Lambda function will send the response to the Destination SQS.
5. If the test is successful the Lambda will send request-ID to the SQL else the error message is logged in Cloudwatch logs.


## Test Scenario-2

### Pre-requisites:
1. An Existing serverless asynchronous application.
2. SQS trigger set for Lambda function
3. Lambda Function (Define in first Test)
4. Destination SQS configured for Lambda function
5. Lambda function to upload to S3 provided here

### Upload to S3 Steps:
1.	SQS send messages with required Payload to create an order.
2.	This triggers the lambda which invokes the API configured and receives the Order_ID in the response and ORDER_ID will be places in another SQS topic.
3.	This triggers another lambda and it cross check the ORDER_ID status against the DynamoDB tables.
4.	Test results will be stored in the S3 bucket.