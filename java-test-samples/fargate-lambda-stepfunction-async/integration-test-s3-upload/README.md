## Description 
Integration Testing - Serverless Asynchronous with s3 Upload

### Pre-requisites:
1. An Existing serverless asynchronous application.
2. SQS trigger set for Lambda function
3. Lambda Function (Define in first Test)
4. Destination SQS configured for Lambda function
5. Lambda function to upload to S3 provided here

### Deploying Lambda:
1.Lambda
  - Application code is deployed as Zip file or executable in the Lambda function code with updated runtime and Handler
2.Environment Variables 
  - Configure the lambda environment variables with API_URL,REGION,TARGET_QUEUE (Queue where the message is to be received)

### Application Flow Steps:
1. SQS to send messages with required Payload.
2. This triggers the lambda which invokes the API configured.
3. Lambda will trigger the API and awaits response.
4. Once the API sends the response the Lambda function will send the response to the Destination SQS.
5. If the test is successful the Lambda will send request-ID to the SQL else the error message is logged in Cloudwatch logs.