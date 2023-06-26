# Asynchronous Integration Test with Lambda Event Listener and DynamoDB

You may use a variety of resource types to create the event listener for your asynchronous system under test ([more about event listeners](../README-ASYNC.md#configure-event-producers-and-event-listeners)). We recommend starting with AWS Lambda and Amazon DynamoDB. DynamoDB creates a persistent storage resource that can enable long running tests or an aggregation of a set of results.

In this pattern, a Lambda function is configured to be an event listener to receive the System Under Test's output data. DynamoDB is configured to be the event listener storage option. In Step 1 in the diagram below, the test establishes a polling pattern with DynamoDB. In Step 2, the test sends input data to the asynchronous system under test. The async system processes the data and in Step 3 the Lambda function receives the data and puts it into DynamoDB. The polling process queries DynamoDB and examines the result. We recommend writing tests for failure conditions including timeouts and malformed requests.

![AWS Lambda and AmazonDynamoDB](../img/lambda-dynamo.png)

[[top]](#asynchronous-integration-test-with-lambda-event-listener-and-dynamodb)

## Review the System Under Test

The System Under Test (SUT) in this example is an asynchronous text processor. It contains a source S3 bucket that receives a text file. A Lambda function is configured to be notified when the putObject event is executed on this bucket. The Lambda function gets the file from the source bucket, transforms the contents of the file to uppercase, then puts the file into a destination S3 bucket.

![S3 to Lambda to S3](../img/s3-lambda-s3.png)

Your goal is to test this asynchronous process. You will use the Lambda Event Listener and DynamoDB test pattern to test the process. You will deploy the following resources:

-   S3 Source Bucket
-   Lambda function text processor
-   S3 Destination Bucket
-   Lambda event listener (test environments only)
-   DynamoDB results storage (test environments only)

[[top]](#asynchronous-integration-test-with-lambda-event-listener-and-dynamodb)

# App

This project contains an AWS Lambda maven application with [AWS Java SDK 2.x](https://github.com/aws/aws-sdk-java-v2) dependencies.

## Prerequisites
The SAM CLI is an extension of the AWS CLI that adds functionality for building and testing serverless applications. It contains features for building your appcation locally, deploying it to AWS, and emulating AWS services locally to support automated unit tests.  

To use the SAM CLI, you need the following tools.

- [Java 17+](https://aws.amazon.com/corretto/)
- [Apache Maven](https://maven.apache.org/)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- [Docker](https://www.docker.com/)

## Building the project
To build the project using local environment use:

```
sam build
```

Or, to build it using the container:

```
sam build -u
```

## Deployment

The generated project contains a default [SAM template](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-function.html) file `template.yaml` where you can 
configure different properties of your lambda function such as memory size and timeout. You might also need to add specific policies to the lambda function
so that it can access other AWS resources.

To deploy the application, you can run the following command:

```
sam deploy --guided
```

See [Deploying Serverless Applications](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-deploying.html) for more info.

[[top]](#asynchronous-integration-test-with-lambda-event-listener-and-dynamodb)

## Run the tests
To run the test to the complete scenario use Maven with the following command:

```
export AWS_SAM_STACK_NAME=async-lambda-dynamodb
mvn test
unset AWS_SAM_STACK_NAME
```

[[top]](#asynchronous-integration-test-with-lambda-event-listener-and-dynamodb)

## Clean-up
```
sam delete
```

[[top]](#asynchronous-integration-test-with-lambda-event-listener-and-dynamodb)
