## Async-sqs-lambda-stepfunction-dynamodb 
A Simple DynamoDB & SQS integration with Spring Boot application and deployed on Fargate.

![async-arch.png](lambda-stepfunction-invoke%2Fdoc%2Fasync-arch.png)

### Description:
The sample Spring boot application written in Java which performs Order Processing operations. AWS serverless services like Amazon API Gateway, ALB, Fargate, DynamoDB, Step Function & SQS being used to host and test the application flow.

### Application
This project contains a Java version 21 maven application with Springboot 3.2.2 and AWS Java SDK 2.17.56 dependencies.

### Pre-requisites
1) SQS Queue with invoke lambda permission
2) SQS trigger set for Lambda function
3) Step function with Dynamodb access
4) DynamoDB tables
5) Table Attributes
   1) order_details ref: src/test/resources/order_details.json
   2) product_details ref: src/test/resources/product_details.json

### Steps:
1) API endpoints are set in API Gateway
2) Containerized application is deployed on ECS cluster as AWS Fargate
3) * Scenario-1:
    1) Create order invocation message placed into SQS
    2) SQS message received from lambda which triggers the step function to create order
    3) Product quantity availability check happens in step function and based on this order creation will be stored into DynamoDB.
   * Scenario-2:
    1) Order Status API request sent to application.
    2) Application backend code connects to DynamoDB and displays status of order.
_________________________________________________________________________________________________________
## Lambda StepFunction Invocation in Application
Incoming message is received in SQS queue which internally triggers the lambda for processing. Step function is integrated in lambda and is executed. Based on the request step function flow executed and data will be stored into DynamoDB tables.

### Java Version
Java-21

### Pre-requisites
1. SQS Queue with invoke lambda permission
2. SQS trigger set for Lambda function
3. Step function with Dynamodb access
4. DynamoDB tables

### Application Flow Steps:
1. SQS queue is to receive messages from the application hosted on AWS Fargate
2. Message placed in SQS triggers the Lambda function
3. Lambda will invoke the pre-defined Step function(refer config.properties)
4. Step function will check for product availability in DynamoDB prodcut_details table, In case product quantity available order status will be set as order placed, Otherwise order rejected will be executed.

_________________________________________________________________________________________________________
## Integration Testing - Serverless Asynchronous

![Serverless async Test Architecture.png](doc%2FServerless%20async%20Test%20Architecture.png)

### Deploying Lambda:
1.Lambda
- Application code is deployed as Zip file or executable in the Lambda function code with updated runtime and Handler

2.Environment Variables
- Configure the lambda environment variables with API_URL,REGION,TARGET_QUEUE (Queue where the message is to be received)

## Test Scenario-1
The scenario being tested involves an automated workflow where messages are sent to an SQS queue, triggering a Lambda function to invoke a configured API. The Lambda function awaits a response from the API and, upon receiving it, processes the response and sends it to another SQS queue. If the test is successful, the Lambda function sends a request ID to an SQL database. However, if the API response is not received as expected, an error message is logged in CloudWatch Logs. This end-to-end test verifies the system's ability to properly handle message processing, API invocations, response handling, and error logging, ensuring reliability and correctness in various scenarios.

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
The scenario being tested involves the end-to-end process of creating an order within the system. Messages are sent to an SQS queue containing the required payload to create an order, initiating the process. Upon message receipt, a Lambda function invokes a configured API to create the order and receives the Order_ID in the response. The Order_ID is then placed in another SQS topic for further processing. Subsequently, another Lambda function is triggered to cross-check the status of the Order_ID against DynamoDB tables. Finally, the test results, including order creation status, are stored in an S3 bucket for analysis and record-keeping.

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