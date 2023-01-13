# Asynchronous System Test with Lambda Event Listener and DynamoDB
You may use a variety of resource types to create the event listener for your asynchronous system under test. We recommend starting with AWS Lambda and Amazon DynamoDB. DynamoDB creates a persistent storage resource that can enable long running tests or an aggregation of a set of results.

In this pattern, a Lambda function is configured to be an event listener to receive the SUT’s output data. DynamoDB is configured to be the event listener storage option. In Step 1 in the diagram below, the test establishes a long polling pattern with DynamoDB. In Step 2, the test sends input data to the asynchronous system under test. The async system processes the data and in Step 3 the the Lambda function receives the data and puts it into DynamoDB. The long poll queries DynamoDB and examines the result. We recommend writing tests for failure conditions including timeouts and malformed requests.

![AWS Lambda and AmazonDynamoDB](../img/lambda-dynamo.png)

The System Under Test (SUT) in this example is an asynchronous text processor. It contains a source S3 bucket that receives a text file. A Lambda function is configured to be notified when the putObject event is executed on this bucket. The Lambda function gets the file from the source bucket, transforms the contents of the file to uppercase, then puts the file into a destination S3 bucket.

![S3 to Lambda to S3](../img/s3-lambda-s3.png)

Your goal is to test this asynchronous process. You will use the Lambda Event Listener and DynamoDB test pattern to test the process. You will deploy the following resources:

* S3 Source Bucket
* Lambda function text processor
* S3 Destination Bucket
* Lambda event listener (test environments only)
* DynamoDB results storage (test environments only)

Build the project

Deploy the resources to the cloud

Run the tests

