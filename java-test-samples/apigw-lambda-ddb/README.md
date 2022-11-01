## Microservice: API Gateway, Lambda Function and Dynamodb Table

### Description

This pattern creates an Amazon API Gateway HTTP API, a AWS Lambda function and a DynamoDB Table using SAM and Java 11.

Important: this application uses various AWS services and there are costs associated with these services after the Free Tier usage - please see the AWS Pricing page for details. You are responsible for any AWS costs incurred.

## Language
This is a Maven project which uses Java 11 and AWS SDK

## Framework
The framework used to deploy the infrastructure is SAM

## Services used
The AWS services used in this pattern are

#### API Gateway - AWS Lambda - DynamoDB

Topology

<img src="docs/TicketTopology.png" alt="topology" width="80%"/>


## Description
The SAM template contains all the information to deploy AWS resources(an API Gateway, a Lambda function and a DynamoDB table) and also the permission required by these service to communicate.

You will be able to create and delete the CloudFormation stack using the CLI commands.

After the stack is created you can send an JSON object using curl or Postman to the URL provided by the API Gateway,
the request will be intercepted by the Lambda function which will persist the object into a DynamoDB table.

The lambda function will return the ID of the inserted object.

## Deployment commands

````
mvn clean package


# create an S3 bucket where the source code will be stored:

aws s3 mb s3://lambda-functions-some-random-letters


# copy the source code located in the target folder:

aws s3 cp target/ticketPublisher.zip s3://lambda-functions-some-random-letters


# SAM will deploy the CloudFormation stack described in the template.yml file:

sam deploy --s3-bucket lambda-functions-some-random-letters --stack-name ticket-stack --capabilities CAPABILITY_IAM


# REMEMBER to DELETE the CloudFormation stack

aws cloudformation delete-stack --stack-name ticket-stack


````

## Testing

To test the endpoint first send data using the following command. Be sure to update the endpoint with endpoint of your stack.

```
curl -X POST https://COPYfromAPIGateway/dev/ticket -H "Content-Type: application/json" -d '{"userId": "231deb432f3dd","description": "My monitor is broken."}' 
```

## Automated Tests
The source code for this sample includes automated tests.
### Running Automated Tests
These tests are run while packaging the lambda function using `mvn clean package` or can be run standalone using `mvn test`.
### Automated Test Framework
[Junit 5](https://junit.org/junit5/) is the primary test framework used to write these tests. A few other libraries and frameworks are used depending on the test case pattern. Please see below. 
### Types of Automated Tests
The sample includes the following tests:

#### Unit Test (TicketFunctionMockTest.java)
The goal of this test is to run a unit test on the handler method of the Lambda function. It uses [Mockito](https://site.mockito.org/) as a mocking framework. All the calls to the Amazon DynamoDB service are mocked using Mockito. 
It also uses [aws-lambda-java-test](https://github.com/aws/aws-lambda-java-libs/tree/master/aws-lambda-java-tests) library. This library helps 
to easily inject `APIGatewayProxyRequestEvent` into the Lambda function's handler method. To know more about how to leverage `aws-lambda-java-test` you can refer to [this](https://aws.amazon.com/blogs/opensource/testing-aws-lambda-functions-written-in-java/) blog.

#### Integration Test (TicketFunctionIntegrationTest.java)
The goal of this test is to demonstrate a test that runs the Lambda function's code locally without mocking any calls to the Amazon DynamoDB service. It assumes that [AWS CLI](https://aws.amazon.com/cli/) is installed locally and that AWS Credentials are stored in ~/.aws/credentials file with default profile.
If your local AWS CLI configuration is different, please update the tests accordingly.

#### Local Test using containers (TicketFunctionContainerTest.java)
The goal of this test is to demonstrate a test that simulates AWS services locally using [localstack](https://github.com/localstack/localstack).  This test uses containers and requires [Docker](https://docs.docker.com/get-docker/) installed locally.
Similar to the integration test above, this test runs Lambda function's code locally but, it integrates with the DynamoDB service that is part of the localstack container image which is running on the local machine. 

#### End-to-End Test (TicketEnd2EndTest.java)
The goal of this test is to run an end-to-end test on AWS. This test assumes the sample stack provided in the sample is deployed to AWS. The stack name is referred in the test class as a String constant.
```
private static final String STACK_NAME = "APIGW-Lambda-DDB-Sample";
```
Please make sure to replace the above with your stack name. This test submits a ATTP request to the API Gateway Endpoint and verifies that the results are reflected in teh DynamoDB database table.


## Cleanup

Run the given command to delete the resources that were created. It might take some time for the CloudFormation stack to get deleted.
```
aws cloudformation delete-stack --stack-name ticket-stack
```

## Requirements

* [Create an AWS account](https://portal.aws.amazon.com/gp/aws/developer/registration/index.html) if you do not already have one and log in. The IAM user that you use must have sufficient permissions to make necessary AWS service calls and manage AWS resources.
* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) installed and configured
* [Git Installed](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* [AWS Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) (AWS SAM) installed